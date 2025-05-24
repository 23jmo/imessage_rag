# Modern LangChain RAG example with ChromaDB, metadata filtering, and prompt hub
# Usage: python -m imessage_insight.test_scripts.langchain_rag_example

import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain import hub
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_DIR = "imessage_insight/chromadb_data"
COLLECTION_ST = "imessage_chunks"
COLLECTION_OAI = "imessage_chunks_openai"
MODEL_ST = "all-MiniLM-L6-v2"

print("\n--- LangChain RAG Example (ChromaDB + LLM, modern API) ---\n")
print("Select embedding model:")
print("  1. SentenceTransformers (all-MiniLM-L6-v2) [default]")
print("  2. OpenAI (text-embedding-ada-002)")
emb_choice = input("Enter 1 or 2: ").strip() or "1"
if emb_choice not in ("1", "2"):
    print("Invalid choice. Using SentenceTransformers.")
    emb_choice = "1"

if emb_choice == "2":
    collection_name = COLLECTION_OAI
    embedding_function = OpenAIEmbeddings()
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    print("Using OpenAI embeddings and GPT-4o.")
else:
    collection_name = COLLECTION_ST
    st_model = SentenceTransformer(MODEL_ST)
    class STEmbedder:
        def embed_query(self, text):
            return st_model.encode([text])[0].tolist()
        def embed_documents(self, texts):
            return [vec.tolist() for vec in st_model.encode(texts)]
    embedding_function = STEmbedder()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    print("Using SentenceTransformers embeddings and GPT-3.5-turbo.")

cutoff_date = input("Enter cutoff date (YYYY-MM-DD or press Enter for no cutoff): ").strip()
if cutoff_date:
    try:
        cutoff_dt = datetime.fromisoformat(cutoff_date)
        cutoff_ts = cutoff_dt.timestamp()
        print(f"Using cutoff: Only retrieving messages after {cutoff_date} (timestamp: {cutoff_ts})")
    except Exception as e:
        print(f"Invalid date format. Proceeding without cutoff. Error: {e}")
        cutoff_ts = None
else:
    cutoff_ts = None

# Build vectorstore and retriever with filter
vectorstore = Chroma(
    collection_name=collection_name,
    persist_directory=CHROMA_DIR,
    embedding_function=embedding_function
)
search_kwargs = {"k": 5}
if cutoff_ts is not None:
    search_kwargs["filter"] = {"start_date_ts": {"$gt": cutoff_ts}}
    print(f"[DEBUG] Applying filter: {search_kwargs['filter']}")
retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

# Use prompt hub for RAG prompt
prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Build the RAG chain using Runnable protocol
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Interactive Q&A loop
while True:
    query = input("\nEnter your question (or 'exit' to quit): ").strip()
    if query.lower() == 'exit':
        break
    # Get retrieved docs directly for debugging
    docs = retriever.get_relevant_documents(query)
    print(f"\n--- Retrieved {len(docs)} Chunks ---")
    if len(docs) == 0 and cutoff_ts is not None:
        print("WARNING: No chunks retrieved with cutoff filter.")
        print("Possible issues:")
        print("- start_date_ts missing or not a float/int in metadata")
        print("- Field name typo (should be 'start_date_ts')")
        print("- Old collection without start_date_ts")
        print("- Vectorstore needs to be rebuilt after metadata changes")
        print("- All chunks are before the cutoff date")
    for i, doc in enumerate(docs):
        meta = doc.metadata
        ts = meta.get("start_date_ts")
        ts_str = f" ({datetime.fromtimestamp(ts).isoformat()})" if isinstance(ts, (float, int)) else ""
        print(f"Chunk {i+1}:")
        print(f"  Metadata: {meta}")
        print(f"  start_date_ts: {ts}{ts_str}")
        print(f"  Text: {doc.page_content[:100]}...\n")
    # Run the RAG chain for the answer
    result = rag_chain.invoke(query)
    print("\n--- Answer ---")
    print(result) 