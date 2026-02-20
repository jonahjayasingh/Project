from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
import sys

DB_DIR = "book_db"
LLM_MODEL = "llava:7b"

print("🧠 Loading vector database...")
embeddings = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

llm = OllamaLLM(model=LLM_MODEL)

print("✅ Ready. Ask your books (type 'exit' to quit).\n")

try:
    while True:
        query = input("Ask: ").strip()
        if query.lower() in {"exit", "quit"}:
            break

        anchored_query = f"In the context of the books provided, {query}"
        docs = db.similarity_search_with_score(anchored_query, k=8)

        if not docs:
            print("Not found in the book.\n")
            continue

        context = "\n\n".join(d.page_content for d, _ in docs)
        
        prompt = f"""You are a strict textbook assistant. Explain concepts clearly.
Answer ONLY using the context below. If not found, say "Not found in the book."

Context:
{context}

Question: {query}
Answer:"""

        print("\n🧠 Thinking...")
        response = llm.invoke(prompt)
        print(f"\nAnswer:\n{response}\n")

except KeyboardInterrupt:
    print("\n👋 Exiting.")
    sys.exit(0)

