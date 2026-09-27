from dotenv import load_dotenv
load_dotenv()


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

model=ChatOpenAI(
    model='gpt-5-nano',
    temperature=0.7,
    max_tokens=1000
)


docs=TextLoader("document_loaders/notes.txt")
data=docs.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=10,
)


chunks = splitter.split_documents(data)

print(len(chunks))


for ch in chunks:
    print(ch.page_content)




template=ChatPromptTemplate.from_messages(
    [("system", "You are a helpful AI Summarizer"),
     ("human","{data}")]
)

prompt=template.format_messages(data=data[0].page_content)

response=model.invoke(prompt)

print(response.content)