import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from tqdm import tqdm

BOOK_DIR = "books"
DB_DIR = "book_db"

def main():
    if not os.path.exists(BOOK_DIR):
        os.makedirs(BOOK_DIR)
        print(f"📁 Created '{BOOK_DIR}' directory. Please add documents and rerun.")
        return

    if not os.listdir(BOOK_DIR):
        print(f"⚠️ No books found in '{BOOK_DIR}'.")
        return

    print("📚 Loading documents...")
    docs = []

    for file in os.listdir(BOOK_DIR):
        path = os.path.join(BOOK_DIR, file)
        try:
            if file.lower().endswith(".pdf"):
                loader = PyPDFLoader(path)
            else:
                loader = TextLoader(path, encoding="utf-8")
            
            loaded = loader.load()
            for d in loaded:
                d.metadata["source_file"] = file
            docs.extend(loaded)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")

    print(f"Loaded {len(docs)} pages.")

    print("✂️ Chunking...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=120,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks.")

    print("🧠 Initializing embeddings...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Clear existing database if it exists to avoid duplicates
    if os.path.exists(DB_DIR):
        print(f"🧹 Clearing existing database in '{DB_DIR}'...")
        shutil.rmtree(DB_DIR)

    print("📦 Building vector database in batches...")
    
    # Process in batches for better stability and progress tracking
    batch_size = 100
    db = None
    
    for i in tqdm(range(0, len(chunks), batch_size), desc="Ingesting chunks"):
        batch = chunks[i : i + batch_size]
        if db is None:
            db = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=DB_DIR,
            )
        else:
            db.add_documents(batch)

    print("\n✅ Ingestion complete. Database is ready!")

if __name__ == "__main__":
    main()
