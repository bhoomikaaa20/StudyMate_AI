from dotenv import load_dotenv
load_dotenv()


from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Python is a programming language.",
        metadata={"source": "doc1", "topic": "python"}
    ),

    Document(
        page_content="Machine learning allows computers to learn from data.",
        metadata={"source": "doc2", "topic": "machine learning"}
    ),

    Document(
        page_content="Deep learning uses neural networks.",
        metadata={"source": "doc3", "topic": "deep learning"}
    )
]



embedding_model=OpenAIEmbeddings()

vector_store=Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory="chroma-database"   
)

result=vector_store.similarity_search("ML allows what?",k=2)

for i in result:
    print(i.page_content)

print("-----------------------------")

retreiver=vector_store.as_retriever()

docs=retreiver.invoke("Whta is ml?")

for i in docs:
    print(i.page_content)


