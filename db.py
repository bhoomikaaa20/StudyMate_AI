from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate


# --------------------------------
# 1. Load existing vector DB
# --------------------------------

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vector_store = Chroma(
    collection_name="transformers",
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
)

print(
    "Documents in Chroma:",
    vector_store._collection.count()
)


# --------------------------------
# 2. MMR Retriever
# --------------------------------

mmr_retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)


# --------------------------------
# 3. LLM
# --------------------------------

llm = ChatOpenAI(
    model="gpt-5-nano"
)


# --------------------------------
# 4. Prompt
# --------------------------------

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


# --------------------------------
# 5. Chat
# --------------------------------

while True:

    query = input("You: ")

    if query.strip() == "0":
        break

    # Retrieve
    docs = mmr_retriever.invoke(query)

    # DEBUG: see what was retrieved
    print("\n========== RETRIEVED DOCUMENTS ==========")

    for i, doc in enumerate(docs):
        print(f"\n--- Document {i + 1} ---")
        print(doc.page_content)

    print("\n=========================================")

    # Create context
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Create prompt
    final_prompt = prompt.invoke({
        "context": context,
        "question": query
    })

    # Generate answer
    response = llm.invoke(final_prompt)

    print(f"\nAI: {response.content}")