from dotenv import load_dotenv
load_dotenv()


from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("transformers.pdf")

docs = loader.load()



embedding_model=OpenAIEmbeddings()

vector_store=Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory="../chroma-database"   
)

result=vector_store.similarity_search("what are transformers",k=2)

for i in result:
    print(i.page_content)

print("-----------------------------")

retreiver=vector_store.as_retriever()

docs=retreiver.invoke("Whta is ml?")

for i in docs:
    print(i.page_content)


