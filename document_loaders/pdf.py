from dotenv import load_dotenv
load_dotenv()


from langchain_community.document_loaders import PyPDFLoader

loader = TextLoader("notes.txt")

docs = loader.load()

print(docs[0])