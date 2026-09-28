from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# 1. Load PDF
loader = PyPDFLoader("document_loaders/transformers.pdf")
data = loader.load()

print("Pages:", len(data))


# 2. Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10
)

chunks = splitter.split_documents(data)

print("Chunks:", len(chunks))


# 3. Create embeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


# 4. Create Chroma vector database
vector_store = Chroma(
    collection_name="transformers",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# 5. Store chunks
vector_store.add_documents(chunks)

print("Chunks stored successfully!")