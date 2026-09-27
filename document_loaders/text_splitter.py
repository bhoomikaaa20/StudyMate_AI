from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

docs = TextLoader("notes2.txt")
data = docs.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=1,
    separators=[""]
)

chunks = splitter.split_documents(data)

print(len(chunks))


for ch in chunks:
    print(ch.page_content)

