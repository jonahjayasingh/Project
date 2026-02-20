"""
AI Service for handling RAG-based chat responses
"""
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import shutil

# Configuration
BASE_PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_PROJECT_DIR, "book_db")
BOOK_DIR = os.path.join(BASE_PROJECT_DIR, "books")
DEFAULT_LLM_MODEL = "llava:7b"
EMBEDDING_MODEL = "nomic-embed-text"


class AIService:
    """Service for AI-powered chat responses using RAG"""
    
    def __init__(self, llm_model=None):
        self.llm_model = llm_model or DEFAULT_LLM_MODEL
        self.embeddings = None
        self.db = None
        self.llm = None
        self.progress = {} # user_id -> percentage
        
    def initialize(self):
        """Initialize the AI service components"""
        try:
            self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
            if os.path.exists(DB_DIR):
                self.db = Chroma(persist_directory=DB_DIR, embedding_function=self.embeddings)
            self.llm = OllamaLLM(model=self.llm_model)
            return True
        except Exception as e:
            print(f"Error initializing AI service: {e}")
            return False
    
    def generate_response(self, user_message, user=None, use_rag=True):
        """
        Generate AI response for user message
        
        Args:
            user_message: The user's input message
            user: The user object requesting the response
            use_rag: Whether to use RAG (retrieval-augmented generation)
        
        Returns:
            str: AI-generated response
        """
        if not self.llm:
            self.initialize()
        
        if not self.llm:
            return "⚠️ AI service is not available. Please make sure Ollama is running."
        
        try:
            if use_rag and self.db:
                return self._generate_rag_response(user_message, user)
            else:
                return self._generate_simple_response(user_message)
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"❌ I encountered an error: {str(e)}"
    
    def _generate_rag_response(self, user_message, user=None):
        """Generate response using RAG with user-specific filtering"""
        print(f"🔍 Using RAG to answer for user {user.username if user else 'Anonymous'}: {user_message[:50]}...")
        
        # Build metadata filter
        # Admin can access everything, users can access their own + global
        search_filter = None
        if user and not user.is_superuser:
            search_filter = {
                "$or": [
                    {"user_id": {"$eq": user.id}},
                    {"is_global": {"$eq": True}}
                ]
            }
        # If user is admin (is_superuser), search_filter remains None
        
        # Perform similarity search
        try:
            print(f"DEBUG: Starting similarity search for {user_message[:20]}...")
            if search_filter:
                docs = self.db.similarity_search_with_score(user_message, k=8, filter=search_filter)
            else:
                docs = self.db.similarity_search_with_score(user_message, k=8)
            print(f"DEBUG: Similarity search complete. Found {len(docs) if docs else 0} documents.")
        except Exception as e:
            print(f"Filter error (falling back to no filter): {e}")
            docs = self.db.similarity_search_with_score(user_message, k=8)
        
        if not docs or len(docs) == 0:
            return "I couldn't find relevant information in the library. Please upload documents."
        
        # Build context
        context_parts = []
        for i, (doc, score) in enumerate(docs):
            source = doc.metadata.get('source_file', 'Unknown')
            context_parts.append(doc.page_content)
        
        context = "\n\n".join(context_parts)
        print("DEBUG: Context built. Invoking LLM...")
        
        prompt = f"""Answer the question using ONLY the context provided below.
Context:
{context}

Question: {user_message}
Answer:"""
        
        response = self.llm.invoke(prompt)
        print("DEBUG: LLM response received.")
        return response
    
    def _generate_simple_response(self, user_message):
        """Generate simple response without RAG"""
        prompt = f"Question: {user_message}\nAnswer:"
        return self.llm.invoke(prompt)
    
    def ingest_documents(self, file_paths, user=None, is_global=False):
        """
        Ingest documents into the vector database with ownership info
        """
        try:
            if not os.path.exists(BOOK_DIR):
                os.makedirs(BOOK_DIR)
            
            docs = []
            for file_path in file_paths:
                filename = os.path.basename(file_path)
                if filename.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding="utf-8")
                
                loaded = loader.load()
                for d in loaded:
                    d.metadata["source_file"] = filename
                    d.metadata["user_id"] = user.id if user else 0
                    d.metadata["is_global"] = is_global
                docs.extend(loaded)
            
            if not docs:
                return False, "No documents loaded."
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
            chunks = splitter.split_documents(docs)
            
            if not self.embeddings:
                self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
            
            # Reset progress for user
            user_id = user.id if user else 0
            self.progress[user_id] = {"percentage": 0, "current_file": "Initializing..."}
            
            # Process in batches to show progress
            batch_size = 5
            total_chunks = len(chunks)
            
            for i in range(0, total_chunks, batch_size):
                batch = chunks[i:i+batch_size]
                # Get the source file of the first chunk in batch for tracking
                current_file = batch[0].metadata.get("source_file", "Unknown")
                
                if self.db is None:
                    # Ensure directory exists and is writable
                    if not os.path.exists(DB_DIR):
                        os.makedirs(DB_DIR, exist_ok=True)
                    
                    self.db = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        persist_directory=DB_DIR,
                    )
                    
                    # Try to force 777 on the new DB to avoid readonly issues on external drives
                    try:
                        for root, dirs, files in os.walk(DB_DIR):
                            for d in dirs: os.chmod(os.path.join(root, d), 0o777)
                            for f in files: os.chmod(os.path.join(root, f), 0o777)
                    except:
                        pass
                else:
                    self.db.add_documents(batch)
                
                # Update progress
                self.progress[user_id] = {
                    "percentage": int(((i + len(batch)) / total_chunks) * 100),
                    "current_file": current_file
                }
            
            # Reset progress once done
            # self.progress[user_id] = 100 # Handled by the loop
            
            return True, f"Successfully ingested {len(docs)} pages."
        except Exception as e:
            print(f"CRITICAL: Ingestion failed: {str(e)}")
            # Cleanup on failure: Remove physical files and database records
            from .models import Document
            for file_path in file_paths:
                # 1. Remove physical file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Cleanup: Removed failed document file: {file_path}")
                    except:
                        pass
                
                # 2. Remove database record
                try:
                    Document.objects.filter(file_path=file_path).delete()
                    print(f"Cleanup: Removed failed document record for: {file_path}")
                except:
                    pass

            if user: 
                self.progress[user.id] = -1 # Error state
            return False, f"Error: {str(e)}"
    
    def get_library_info(self, user=None):
        """Get information about the current library for a user"""
        from .models import Document
        if user and user.is_superuser:
            # Admins see everything
            docs = Document.objects.all()
        elif user:
            # Users see their own + global
            from django.db.models import Q
            docs = Document.objects.filter(Q(user=user) | Q(is_global=True))
        else:
            return []
            
        return [{
            'id': doc.id,
            'name': doc.name,
            'is_global': doc.is_global,
            'owner': doc.user.username if doc.user else 'Global'
        } for doc in docs]

    def delete_document_vectors(self, filename):
        """Remove document chunks from the vector database"""
        if not self.db:
            self.initialize()
        
        if self.db:
            try:
                # Delete by filename metadata
                self.db.delete(where={"source_file": filename})
                return True
            except Exception as e:
                print(f"Error deleting vectors for {filename}: {e}")
                return False
        return False

    def clear_library(self, user=None):
        """Clear user's documents (admins can clear all)"""
        from .models import Document
        try:
            if user and user.is_superuser:
                # Complete reset for admin
                Document.objects.all().delete()
                
                # Close reference to db before deleting files to avoid locks
                self.db = None
                
                if os.path.exists(DB_DIR):
                    import shutil
                    import time
                    # Small delay to ensure any file locks are released
                    time.sleep(0.5)
                    shutil.rmtree(DB_DIR, ignore_errors=True)
                
                return True, "Global library and vector database cleared."
            elif user:
                # Selective clear for regular users
                user_docs = Document.objects.filter(user=user)
                for doc in user_docs:
                    # Remove vectors
                    self.delete_document_vectors(doc.name)
                    # Remove physical file
                    if os.path.exists(doc.file_path):
                        try:
                            os.remove(doc.file_path)
                        except Exception as e:
                            print(f"Error removing file {doc.file_path}: {e}")
                
                user_docs.delete()
                return True, "Your personal library and associated files cleared."
        except Exception as e:
            return False, f"Error clearing library: {str(e)}"
            
        return False, "Unauthorized or invalid user."

# Global instance
ai_service = AIService()
