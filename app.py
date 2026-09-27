from dotenv import load_dotenv
load_dotenv()


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader


model=ChatOpenAI(
    model='gpt-5-nano',
    temperature=0.7,
    max_tokens=1000
)

docs=TextLoader("document_loaders/notes.txt")
data=docs.load()


template=ChatPromptTemplate.from_messages(
    [("system", "You are a helpful AI Summarizer"),
     ("human","{data}")]
)

prompt=template.format_messages(data=data[0].page_content)

response=model.invoke(prompt)

print(response.content)