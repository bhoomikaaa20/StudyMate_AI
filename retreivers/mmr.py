from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings



docs = [
    Document(page_content="Python is a high-level programming language known for its simple and readable syntax."),
    Document(page_content="Python is widely used in data science, machine learning, and artificial intelligence."),
    Document(page_content="Python supports object-oriented, procedural, and functional programming paradigms."),
    Document(page_content="Popular Python libraries include NumPy for numerical computing and Pandas for data analysis."),
    Document(page_content="Python applications can be developed using frameworks such as Django and Flask for web development."),
]


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_store=Chroma.from_documents(docs,embeddings)


similarity_search_docs=vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k":3}
)

similarity_docs=similarity_search_docs.invoke("What are python libraries")


print("============Similarity search results==============")

for i in similarity_docs:
    print(i.page_content)



mmr_search_docs=vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k":3}
)

mmr_docs=mmr_search_docs.invoke("What are python libraries")

print("============MMR search results==============")


for i in mmr_docs:
    print(i.page_content)
