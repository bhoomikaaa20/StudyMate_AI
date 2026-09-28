from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# Load PDF
loader = PyPDFLoader(
    "document_loaders/transformers.pdf"
)

data = loader.load()

print("Pages:", len(data))


# Split
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(data)

print("Chunks:", len(chunks))


# Embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# Create vector DB and store chunks
vector_store = Chroma.from_documents(
    documents=chunks,
    collection_name="transformers",
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print(
    "Documents in Chroma:",
    vector_store._collection.count()
)

print("Chunks stored successfully!")