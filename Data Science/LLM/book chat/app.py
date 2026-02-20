import streamlit as st
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

# --- CONFIGURATION ---
DB_DIR = "book_db"
BOOK_DIR = "books"
LLM_MODEL = "llava:7b"  # User's current model
EMBEDDING_MODEL = "nomic-embed-text"

# --- UI SETUP ---
st.set_page_config(
    page_title="Nexus Library | AI Scholar",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Chat bubbles */
    .stChatMessage {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
        backdrop-filter: blur(5px);
    }
    
    /* Input styling */
    .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(96, 165, 250, 0.3) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #60a5fa !important;
        font-weight: 600 !important;
    }
    
    /* Glowing accents */
    .glow-text {
        text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
    }
    
    .status-card {
        padding: 20px;
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def get_vector_db():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    if os.path.exists(DB_DIR):
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return None

def ingest_docs(uploaded_files):
    if not os.path.exists(BOOK_DIR):
        os.makedirs(BOOK_DIR)
    
    docs = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(BOOK_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if uploaded_file.name.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        else:
            loader = TextLoader(file_path, encoding="utf-8")
        
        loaded = loader.load()
        for d in loaded:
            d.metadata["source_file"] = uploaded_file.name
        docs.extend(loaded)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR,
    )
    return db

# --- MAIN UI ---

st.sidebar.markdown("<h1 class='glow-text'>Nexus Library</h1>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# File Upload Section
st.sidebar.subheader("📚 Book Management")
uploaded_files = st.sidebar.file_uploader("Upload books (PDF/TXT)", accept_multiple_files=True)
if st.sidebar.button("⚡ Ingest Library"):
    if uploaded_files:
        with st.status("🏗️ Building Library...", expanded=True) as status:
            db = ingest_docs(uploaded_files)
            status.update(label="✅ Library Synced!", state="complete", expanded=False)
            st.rerun()
    else:
        st.sidebar.warning("Please upload files first.")

# Library Statistics
if os.path.exists(BOOK_DIR):
    books = os.listdir(BOOK_DIR)
    st.sidebar.markdown(f"**Current Books ({len(books)}):**")
    for b in books:
        st.sidebar.markdown(f"- `{b}`")

st.markdown("<h1 class='glow-text'>Scholar Assistant</h1>", unsafe_allow_html=True)
st.markdown("Query your personal library using AI-powered RAG.")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask a question about your books..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        db = get_vector_db()
        
        if not db:
            st.error("No library found. Please upload and ingest books in the sidebar.")
        else:
            # Retrieval
            # Anchoring based on content (could be improved)
            anchored_query = f"In the context of the provided books, {prompt}"
            docs = db.similarity_search_with_score(anchored_query, k=8)
            
            if not docs:
                full_response = "I couldn't find any relevant information in your library."
                response_placeholder.markdown(full_response)
            else:
                context = "\n\n".join(d.page_content for d, _ in docs)
                sources = list(set(d.metadata.get("source_file", "Unknown") for d, _ in docs))
                
                system_prompt = f"""You are a strict academic assistant. 
Explain concepts clearly in simple steps.
Prefer short paragraphs and include small code examples when relevant.
Answer ONLY using the context below. If the answer isn't there, say "Not found in the library."

Context:
{context}
"""
                
                llm = OllamaLLM(model=LLM_MODEL)
                
                # Streaming effect (simulated since OllamaLLM streaming in Streamlit can be tricky with specific versions)
                # For real streaming, we'd use a callback handler
                with st.spinner("Analyzing library..."):
                    full_response = llm.invoke(f"{system_prompt}\n\nQuestion: {prompt}\nAnswer:")
                
                response_placeholder.markdown(full_response)
                
                # Show sources
                with st.expander("🔍 View Sources"):
                    for i, (d, score) in enumerate(docs):
                        st.markdown(f"**Source {i+1}:** {d.metadata.get('source_file', 'N/A')} (Score: {score:.2f})")
                        st.caption(d.page_content[:200] + "...")
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})

# Help Footer
st.sidebar.markdown("---")
st.sidebar.caption("Powered by Ollama & LangChain")
