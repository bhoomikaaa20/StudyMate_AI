import os
import hashlib
import tempfile

import streamlit as st

from dotenv import load_dotenv

from ui import components as ui


load_dotenv()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="StudyMate AI · Chat with your documents",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ui.load_styles()


# Show a loading screen while the heavy AI libraries import
# (only slow on the first run — Python caches them afterwards)
boot_screen = st.empty()

boot_screen.markdown(
    ui.loading_screen(),
    unsafe_allow_html=True
)


from openai import AuthenticationError

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate


# =========================================================
# EMBEDDING MODEL
# =========================================================

@st.cache_resource(show_spinner=False)
def get_embeddings():

    return OpenAIEmbeddings(
        model="text-embedding-3-small"
    )


# =========================================================
# VECTOR DATABASE
# =========================================================

@st.cache_resource(show_spinner=False)
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

@st.cache_resource(show_spinner=False)
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


SUGGESTED_QUESTIONS = [
    "What is the Transformer architecture?",
    "How does multi-head attention work?",
    "Why use positional encoding?",
    "Summarize the key ideas of this document.",
]


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "processed_files" not in st.session_state:

    st.session_state.processed_files = set()


if "upload_notice" not in st.session_state:

    st.session_state.upload_notice = None


def queue_question(question):

    st.session_state.pending_query = question


def on_chat_submit():

    queue_question(st.session_state.chat_input)


def clear_chat():

    st.session_state.messages = []


def friendly_error(error):

    # Avoid echoing raw API errors, which can include a partial API key
    if isinstance(error, AuthenticationError):

        return (
            "OpenAI rejected the API key. Please set a valid "
            "OPENAI_API_KEY in your .env file and restart the app."
        )

    return f"Something went wrong: {type(error).__name__}"


# =========================================================
# PDF PROCESSING
# =========================================================

def process_pdf(uploaded_file):

    # ---------------------------------------------
    # Create unique hash for uploaded file
    # ---------------------------------------------

    file_bytes = uploaded_file.getvalue()

    file_hash = hashlib.md5(
        file_bytes
    ).hexdigest()


    if file_hash in st.session_state.processed_files:

        return {"status": "duplicate"}


    # ---------------------------------------------
    # Save uploaded file temporarily
    # ---------------------------------------------

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(file_bytes)

        temp_path = temp_file.name


    try:

        # Imported here, not at the top: both packages pull in
        # torch/transformers, which would add 15-45s to every app start
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # Load PDF
        loader = PyPDFLoader(
            temp_path
        )

        data = loader.load()


        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = splitter.split_documents(
            data
        )


        # Add metadata
        for chunk in chunks:

            chunk.metadata["source"] = (
                uploaded_file.name
            )


        # Create unique IDs
        ids = [
            f"{file_hash}_{i}"
            for i in range(len(chunks))
        ]


        # Store in Chroma
        vector_store.add_documents(
            documents=chunks,
            ids=ids
        )


        # Mark as processed
        st.session_state.processed_files.add(
            file_hash
        )


        return {
            "status": "success",
            "file_name": uploaded_file.name,
            "pages": len(data),
            "chunks": len(chunks),
            "total_vectors": vector_store._collection.count()
        }


    finally:

        # Delete temporary file
        if os.path.exists(temp_path):

            os.remove(temp_path)


# =========================================================
# RAG ANSWER
# =========================================================

def answer_question(query):

    # Retrieve documents
    docs = retriever.invoke(query)


    # Create context
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )


    # Generate prompt
    final_prompt = prompt.invoke(
        {
            "context": context,
            "question": query
        }
    )

    return docs, final_prompt


def stream_answer(final_prompt, placeholder):

    for chunk in llm.stream(final_prompt):

        if chunk.content:

            placeholder.empty()

            yield chunk.content


def render_message(message):

    avatar = (
        ":material/person:"
        if message["role"] == "user"
        else ":material/auto_awesome:"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            with st.expander(
                f"🔎 Sources · {len(message['sources'])} retrieved chunks"
            ):

                ui.sources(
                    message["sources"]
                )


# =========================================================
# LAYOUT
# =========================================================

vector_count = vector_store._collection.count()

boot_screen.empty()

pending_query = st.session_state.pop(
    "pending_query",
    None
)

ui.navbar(vector_count)

ui.hero()

ui.stats(
    vector_count=vector_count,
    documents=len(st.session_state.processed_files),
    questions=sum(
        m["role"] == "user"
        for m in st.session_state.messages
    ) + (1 if pending_query else 0)
)


left, right = st.columns(
    [1, 2.15],
    gap="large"
)


# =========================================================
# LEFT: KNOWLEDGE BASE
# =========================================================

with left:

    with st.container(key="kb_card"):

        ui.card_header(
            "📄",
            "Knowledge Base",
            "Add a PDF to expand what StudyMate knows.",
            pill=f"{vector_count:,} chunks"
        )

        uploaded_file = st.file_uploader(
            "Upload a PDF",
            type=["pdf"]
        )


        if uploaded_file is not None:

            if st.button(
                "Process PDF",
                type="primary",
                icon=":material/bolt:",
                width="stretch"
            ):

                with st.spinner(
                    "Reading, chunking and embedding your PDF..."
                ):

                    try:

                        st.session_state.upload_notice = process_pdf(
                            uploaded_file
                        )

                    except Exception as error:

                        st.session_state.upload_notice = {
                            "status": "error",
                            "message": friendly_error(error)
                        }

                st.rerun()

        else:

            st.session_state.upload_notice = None


        notice = st.session_state.upload_notice

        if notice:

            if notice["status"] == "success":

                ui.process_result(
                    notice["file_name"],
                    notice["pages"],
                    notice["chunks"],
                    notice["total_vectors"]
                )

            elif notice["status"] == "duplicate":

                st.info(
                    "This PDF has already been processed.",
                    icon=":material/info:"
                )

            else:

                st.error(
                    f"Could not process this PDF: {notice['message']}",
                    icon=":material/error:"
                )


    st.write("")


    with st.container(key="pipeline_card"):

        ui.card_header(
            "⚙️",
            "How it works",
            pill="RAG pipeline"
        )

        ui.pipeline_steps()


# =========================================================
# RIGHT: CHAT
# =========================================================

with right:

    with st.container(key="chat_card"):

        head, action = st.columns(
            [4, 1],
            vertical_alignment="center"
        )

        with head:

            ui.card_header(
                "💬",
                "Ask StudyMate",
                "Answers are grounded only in your documents."
            )

        with action:

            st.button(
                "Clear chat",
                icon=":material/delete_sweep:",
                on_click=clear_chat,
                width="stretch",
                disabled=not st.session_state.messages
            )


        chat_box = st.container(
            height=560,
            border=False,
            key="chat_scroll"
        )


        with chat_box:

            # -------------------------------------
            # Empty state with suggestions
            # -------------------------------------

            if not st.session_state.messages and not pending_query:

                ui.empty_state()

                cols = st.columns(2)

                for i, question in enumerate(SUGGESTED_QUESTIONS):

                    cols[i % 2].button(
                        question,
                        key=f"suggest_{i}",
                        on_click=queue_question,
                        args=(question,),
                        width="stretch"
                    )


            # -------------------------------------
            # Chat history
            # -------------------------------------

            for message in st.session_state.messages:

                render_message(message)


            # -------------------------------------
            # New question
            # -------------------------------------

            if pending_query:

                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": pending_query
                    }
                )

                render_message(
                    st.session_state.messages[-1]
                )


                with st.chat_message(
                    "assistant",
                    avatar=":material/auto_awesome:"
                ):

                    try:

                        with st.spinner(
                            "Searching your documents..."
                        ):

                            docs, final_prompt = answer_question(
                                pending_query
                            )


                        placeholder = st.empty()

                        placeholder.markdown(
                            ui.thinking(),
                            unsafe_allow_html=True
                        )

                        try:

                            answer = st.write_stream(
                                stream_answer(
                                    final_prompt,
                                    placeholder
                                )
                            )

                        except Exception:

                            # Fall back to a regular call if streaming is unavailable
                            placeholder.empty()

                            answer = llm.invoke(
                                final_prompt
                            ).content

                            st.markdown(answer)


                        sources = [
                            {
                                "content": doc.page_content,
                                "source": doc.metadata.get("source", "Unknown"),
                                "page": doc.metadata.get("page")
                            }
                            for doc in docs
                        ]


                        # Show retrieved chunks
                        with st.expander(
                            f"🔎 Sources · {len(sources)} retrieved chunks"
                        ):

                            ui.sources(sources)


                        # Save assistant response
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources
                            }
                        )

                    except Exception as error:

                        st.error(
                            friendly_error(error),
                            icon=":material/error:"
                        )


        # -----------------------------------------
        # Chat input
        # -----------------------------------------

        st.chat_input(
            "Ask a question about your documents...",
            key="chat_input",
            on_submit=on_chat_submit
        )

        st.markdown(
            '<div class="sm-input-hint">StudyMate answers only from your '
            'documents · Press Enter to send</div>',
            unsafe_allow_html=True
        )


ui.footer()
