from dotenv import load_dotenv
load_dotenv()


from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://en.wikipedia.org/wiki/Sai_Pallavi")

docs = loader.load()

print(docs[0].page_content)