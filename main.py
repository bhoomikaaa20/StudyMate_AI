from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings,ChatOpenAI
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

embedding_model=OpenAIEmbeddings()

vector_store=Chroma.from_documents(
    embedding=embedding_model,
    persist_directory="chroma-database"   
)


mmr_retreiver=vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k":3,
        "fetch_k":3,
        "lambda_mult":0.5
    }

)


llm=ChatOpenAI(
    model='gpt-5-nano'
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful AI assistant.

Use ONLY the provided context to answer the question.

If the answer is not present in the context,
say: "I could not find the answer in the document."
"""
        ),
        (
            "human",
            """Context:
{context}

Question:
{question}"""
        )
    ]
)

print("RAG SYSTEM CREATED")

print("PRESS 0 TO EXIT")

while True: 
    query=input("You:")
    if query.strip()=="0":
        exit
    else:
        docs=mmr_retreiver.invoke(query)

        context="\n\n".join(
            [doc.page_content for doc in docs]
        )

        final_prompt=prompt.invoke(
            context=context,
            question=query
        )

        response=llm.invoke(final_prompt)

        print(f"\n AI:{response.content}")




