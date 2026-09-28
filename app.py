import os
import hashlib
import tempfile

import streamlit as st

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("📚 StudyMate AI")
st.caption("Upload a PDF and ask questions about it using RAG.")


# =========================================================
# EMBEDDING MODEL
# =========================================================

@st.cache_resource
def get_embeddings():

    return OpenAIEmbeddings(
        model="text-embedding-3-small"
    )


# =========================================================
# VECTOR DATABASE
# =========================================================

@st.cache_resource
def get_vector_store():

    embeddings = get_embeddings()

    return Chroma(
        collection_name="transformers",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )


vector_store = get_vector_store()


# =========================================================
# LLM
# =========================================================

@st.cache_resource
def get_llm():

    return ChatOpenAI(
        model="gpt-5-nano"
    )


llm = get_llm()


# =========================================================
# RETRIEVER
# =========================================================

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 3,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)


# =========================================================
# PROMPT
# =========================================================

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


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "processed_files" not in st.session_state:

    st.session_state.processed_files = set()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )


    if uploaded_file is not None:

        st.success(
            f"Selected: {uploaded_file.name}"
        )

        if st.button(
            "Process PDF",
            type="primary",
            use_container_width=True
        ):

            # ---------------------------------------------
            # Create unique hash for uploaded file
            # ---------------------------------------------

            file_bytes = uploaded_file.getvalue()

            file_hash = hashlib.md5(
                file_bytes
            ).hexdigest()


            if file_hash in st.session_state.processed_files:

                st.info(
                    "This PDF has already been processed."
                )

            else:

                with st.spinner(
                    "Processing PDF..."
                ):

                    # -------------------------------------
                    # Save uploaded file temporarily
                    # -------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(file_bytes)

                        temp_path = temp_file.name


                    try:

                        # ---------------------------------
                        # Load PDF
                        # ---------------------------------

                        loader = PyPDFLoader(
                            temp_path
                        )

                        data = loader.load()


                        # ---------------------------------
                        # Split into chunks
                        # ---------------------------------

                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=500,
                            chunk_overlap=50
                        )

                        chunks = splitter.split_documents(
                            data
                        )


                        # ---------------------------------
                        # Add metadata
                        # ---------------------------------

                        for chunk in chunks:

                            chunk.metadata["source"] = (
                                uploaded_file.name
                            )


                        # ---------------------------------
                        # Create unique IDs
                        # ---------------------------------

                        ids = [
                            f"{file_hash}_{i}"
                            for i in range(len(chunks))
                        ]


                        # ---------------------------------
                        # Store in Chroma
                        # ---------------------------------

                        vector_store.add_documents(
                            documents=chunks,
                            ids=ids
                        )


                        # ---------------------------------
                        # Mark as processed
                        # ---------------------------------

                        st.session_state.processed_files.add(
                            file_hash
                        )


                        st.success(
                            "PDF processed successfully!"
                        )

                        st.write(
                            f"Pages: {len(data)}"
                        )

                        st.write(
                            f"Chunks: {len(chunks)}"
                        )

                        st.write(
                            f"Total vectors: "
                            f"{vector_store._collection.count()}"
                        )


                    finally:

                        # Delete temporary file
                        if os.path.exists(temp_path):

                            os.remove(temp_path)


    st.divider()


    st.subheader("📊 Vector Database")

    st.write(
        f"Stored chunks: "
        f"**{vector_store._collection.count()}**"
    )


    if st.button(
        "Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

query = st.chat_input(
    "Ask a question about your documents..."
)


if query:

    # ---------------------------------------------
    # Display user question
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):

        st.markdown(query)


    # ---------------------------------------------
    # Retrieve documents
    # ---------------------------------------------

    with st.spinner(
        "Searching your documents..."
    ):

        docs = retriever.invoke(query)


    # ---------------------------------------------
    # Create context
    # ---------------------------------------------

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )


    # ---------------------------------------------
    # Generate prompt
    # ---------------------------------------------

    final_prompt = prompt.invoke(
        {
            "context": context,
            "question": query
        }
    )


    # ---------------------------------------------
    # Ask LLM
    # ---------------------------------------------

    with st.spinner(
        "Generating answer..."
    ):

        response = llm.invoke(
            final_prompt
        )


    answer = response.content


    # ---------------------------------------------
    # Display answer
    # ---------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)


        # -----------------------------------------
        # Show retrieved chunks
        # -----------------------------------------

        with st.expander(
            "🔎 View retrieved chunks"
        ):

            for i, doc in enumerate(docs):

                st.markdown(
                    f"**Chunk {i + 1}**"
                )

                st.write(
                    doc.page_content
                )

                st.caption(
                    f"Source: "
                    f"{doc.metadata.get('source', 'Unknown')}"
                )


    # ---------------------------------------------
    # Save assistant response
    # ---------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )