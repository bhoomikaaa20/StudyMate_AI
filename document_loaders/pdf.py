from dotenv import load_dotenv
load_dotenv()


from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("transformers.pdf")

docs = loader.load()

print(docs[2].page_content)