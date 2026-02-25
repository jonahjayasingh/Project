"""
STRICT RAG AI Service — Answers ONLY from uploaded books
Uses Ollama + Chroma + LangChain
"""

import os
import time
import shutil

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ================= CONFIGURATION =================

BASE_PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_PROJECT_DIR, "book_db")
BOOK_DIR = os.path.join(BASE_PROJECT_DIR, "books")

DEFAULT_LLM_MODEL = "qwen2.5:3b"
EMBEDDING_MODEL = "nomic-embed-text"

RELEVANCE_THRESHOLD = 0.6   # Higher = stricter grounding


# ================= SERVICE CLASS =================

class AIService:
    """AI-powered strict RAG chat service (book-only answers)"""

    def __init__(self, llm_model=None):
        self.llm_model = llm_model or DEFAULT_LLM_MODEL
        self.embeddings = None
        self.db = None
        self.llm = None
        self.progress = {}   # user_id -> progress info

    # -------------------------------------------------
    # Initialization
    # -------------------------------------------------

    def initialize(self):

        try:
            self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

            if os.path.exists(DB_DIR):
                self.db = Chroma(
                    persist_directory=DB_DIR,
                    embedding_function=self.embeddings
                )

            # Temperature 0 = deterministic, no creativity
            self.llm = OllamaLLM(
                model=self.llm_model,
                temperature=0
            )

            return True

        except Exception as e:
            print(f"Initialization error: {e}")
            return False

    # -------------------------------------------------
    # Main Response
    # -------------------------------------------------

    def generate_response(self, user_message, user=None, use_rag=True):

        if not self.llm:
            self.initialize()

        if not self.llm:
            return "⚠️ Ollama is not running."

        try:
            if use_rag and self.db:
                return self._generate_rag_response(user_message, user)
            else:
                return self._generate_simple_response(user_message)

        except Exception as e:
            print(f"Generation error: {e}")
            return f"❌ Error: {str(e)}"

    # -------------------------------------------------
    # STRICT RAG RESPONSE (BOOK-ONLY)
    # -------------------------------------------------

    def _generate_rag_response(self, user_message, user=None):

        print(f"🔎 RAG query: {user_message[:60]}")

        # ---------- Metadata filter ----------
        search_filter = None

        if user and not user.is_superuser:
            search_filter = {
                "$or": [
                    {"user_id": {"$eq": user.id}},
                    {"is_global": {"$eq": True}}
                ]
            }

        # ---------- Similarity search ----------
        try:
            if search_filter:
                docs = self.db.similarity_search_with_score(
                    user_message, k=8, filter=search_filter
                )
            else:
                docs = self.db.similarity_search_with_score(user_message, k=8)

        except Exception as e:
            print(f"Filter failed, fallback search: {e}")
            docs = self.db.similarity_search_with_score(user_message, k=8)

        if not docs:
            return "This information is not available in the provided documents."

        # ---------- Relevance filtering ----------
        filtered_docs = [
            doc for doc, score in docs
            if score >= RELEVANCE_THRESHOLD
        ]

        if not filtered_docs:
            return "This information is not available in the provided documents."

        # ---------- Build context ----------
        context = "\n\n".join(d.page_content for d in filtered_docs)

        # ---------- STRICT PROMPT ----------
        prompt = f"""
You are a question-answering assistant.

STRICT RULES:
- Answer ONLY using the information from the context below.
- DO NOT use outside knowledge.
- DO NOT guess or infer.
- If the answer is not explicitly stated in the context,
  respond EXACTLY with:
  "This information is not available in the provided documents."

Context:
{context}

Question: {user_message}

Answer:
"""

        return self.llm.invoke(prompt)

    # -------------------------------------------------
    # Simple LLM (No RAG)
    # -------------------------------------------------

    def _generate_simple_response(self, user_message):
        prompt = f"Question: {user_message}\nAnswer:"
        return self.llm.invoke(prompt)

    # -------------------------------------------------
    # Document Ingestion
    # -------------------------------------------------

    def ingest_documents(self, file_paths, user=None, is_global=False):

        try:
            os.makedirs(BOOK_DIR, exist_ok=True)

            docs = []

            for file_path in file_paths:
                filename = os.path.basename(file_path)

                if filename.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding="utf-8")

                loaded_docs = loader.load()

                for d in loaded_docs:
                    # Lowercase content as per user request
                    d.page_content = d.page_content.lower()
                    d.metadata["source_file"] = filename.lower()
                    d.metadata["user_id"] = user.id if user else 0
                    d.metadata["is_global"] = is_global

                docs.extend(loaded_docs)

            if not docs:
                return False, "No documents loaded."

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=150
            )

            chunks = splitter.split_documents(docs)

            if not self.embeddings:
                self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

            user_id = user.id if user else 0
            self.progress[user_id] = {"percentage": 0, "file": "Starting"}

            batch_size = 5
            total = len(chunks)

            for i in range(0, total, batch_size):
                batch = chunks[i:i + batch_size]
                current_file = batch[0].metadata.get("source_file", "Unknown")

                if self.db is None:
                    os.makedirs(DB_DIR, exist_ok=True)

                    self.db = Chroma.from_documents(
                        documents=batch,
                        embedding=self.embeddings,
                        persist_directory=DB_DIR,
                    )
                else:
                    self.db.add_documents(batch)

                percent = int(((i + len(batch)) / total) * 100)

                self.progress[user_id] = {
                    "percentage": percent,
                    "current_file": current_file
                }

            return True, f"Ingested {len(docs)} pages."

        except Exception as e:
            print(f"Ingestion failed: {e}")
            if user:
                self.progress[user.id] = -1
            return False, str(e)

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

    # -------------------------------------------------
    # Delete vectors for a file
    # -------------------------------------------------

    def delete_document_vectors(self, filename):

        if not self.db:
            self.initialize()

        try:
            self.db.delete(where={"source_file": filename})
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False

    # -------------------------------------------------
    # Clear library (selective for users, complete for admin)
    # -------------------------------------------------

    def clear_library(self, user=None):
        from .models import Document
        try:
            if user and user.is_superuser:
                # Complete reset for admin
                Document.objects.all().delete()
                self.db = None
                if os.path.exists(DB_DIR):
                    time.sleep(0.5)
                    shutil.rmtree(DB_DIR, ignore_errors=True)
                return True, "Global library and vector database cleared."
            elif user:
                # Selective clear for regular users
                user_docs = Document.objects.filter(user=user)
                for doc in user_docs:
                    self.delete_document_vectors(doc.name)
                    if os.path.exists(doc.file_path):
                        try:
                            os.remove(doc.file_path)
                        except:
                            pass
                user_docs.delete()
                return True, "Your personal library and associated files cleared."
        except Exception as e:
            return False, f"Error clearing library: {str(e)}"
            
        return False, "Unauthorized or invalid user."
    

# ================= GLOBAL INSTANCE =================

ai_service = AIService()