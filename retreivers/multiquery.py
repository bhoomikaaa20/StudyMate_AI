from dotenv import load_dotenv
load_dotenv()


from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_classic.retrievers.multi_query import MultiQueryRetriever


# -----------------------------
# 1. Load the embedding model
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------
# 2. Load your vector database
# -----------------------------
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)


# -----------------------------
# 3. Create normal retriever
# -----------------------------
base_retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3
    }
)


# -----------------------------
# 4. Create LLM
# -----------------------------
llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0
)


# -----------------------------
# 5. Create MultiQueryRetriever
# -----------------------------
retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm
)


# -----------------------------
# 6. Ask a question
# -----------------------------
query = "What are large language models?"

docs = retriever.invoke(query)


# -----------------------------
# 7. Print results
# -----------------------------
print("\n" + "=" * 60)
print("MULTI QUERY RETRIEVER RESULTS")
print("=" * 60)

for i, doc in enumerate(docs, start=1):
    print(f"\nDocument {i}")
    print("-" * 60)
    print(doc.page_content)

    print("\nMetadata:")
    print(doc.metadata)