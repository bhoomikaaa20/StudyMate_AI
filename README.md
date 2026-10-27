# 📚 StudyMate AI

### AI-Powered Study Assistant for Your Documents

**StudyMate AI** is an AI-powered study assistant that allows students to upload their study materials as PDFs and interact with them through a conversational interface.

Instead of manually searching through lengthy lecture notes, textbooks, or study materials, students can simply **ask questions about their documents and receive relevant, context-aware answers**.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from the uploaded documents before generating an answer with an LLM.

---

## 🎯 Problem

Students often spend a significant amount of time searching through large PDFs and lecture notes to find specific information.

For example, if a student has a 100-page Machine Learning document and wants to know:

> *"What is the difference between Ridge and Lasso regression?"*

they would normally have to search through the document manually.

StudyMate AI makes this process easier by allowing students to simply ask the question and get an answer based on their study material.

---

## 💡 Solution

StudyMate AI transforms static study documents into an **interactive AI-powered knowledge base**.

The user can:

**Upload → Process → Ask → Retrieve → Get an Answer**

The system searches the uploaded document for relevant information and uses that information to generate the response.

This makes studying more interactive and reduces the effort required to find information within lengthy documents.

---

## ✨ Key Features

- 📄 **PDF Upload** – Upload lecture notes, textbooks, research papers, and other study materials.
- 💬 **Interactive AI Chat** – Ask natural-language questions about your documents.
- 🔍 **Semantic Search** – Find relevant information based on meaning rather than only exact keywords.
- 🧠 **RAG-Based Question Answering** – Retrieves relevant document information before generating an answer.
- 🎯 **Relevant Context Retrieval** – Uses MMR-based retrieval to improve the relevance and diversity of retrieved information.
- 🤖 **AI-Powered Responses** – Generates answers using OpenAI's GPT-5-nano.
- 🔎 **Retrieved Content Visibility** – View the document sections used to generate an answer.
- ♻️ **Duplicate Document Detection** – Prevents the same PDF from being processed repeatedly.
- 💾 **Persistent Vector Storage** – Stores document embeddings using ChromaDB.
- 🧹 **Chat Management** – Clear the conversation and start a new study session.

---

## 🧠 How It Works

StudyMate AI follows a **Retrieval-Augmented Generation (RAG)** approach.

```text
        📄 Study Material
               │
               ▼
        Document Processing
               │
               ▼
       Text → Embeddings
               │
               ▼
          🗃️ ChromaDB
               │
               │
        💬 Student Question
               │
               ▼
       🔍 Relevant Retrieval
               │
               ▼
       📚 Relevant Context
               │
               ▼
          🤖 LLM
               │
               ▼
         💡 AI Answer
```

The document is converted into searchable representations and stored in a vector database.

When a student asks a question, StudyMate AI retrieves the most relevant information from the document and provides it to the language model as context.

The model then generates an answer based on the retrieved study material.

---

## 🎓 Who Is It For?

StudyMate AI is designed primarily for **students and learners** who work with large amounts of digital study material.

### Use cases include:

- 📚 University lecture notes
- 📝 Exam preparation
- 📖 Textbooks
- 🧪 Lab manuals
- 📄 Research papers
- 💻 Technical documentation
- 🎓 Course materials
- 📋 Certification preparation

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python** | Core application development |
| **Streamlit** | Interactive web interface |
| **LangChain** | RAG and LLM application framework |
| **OpenAI GPT-5-nano** | AI response generation |
| **OpenAI Embeddings** | Semantic representation of documents |
| **ChromaDB** | Vector database |
| **PyPDF** | PDF document processing |

---

## 🌟 What Makes StudyMate AI Useful?

Traditional document search mainly looks for matching words.

StudyMate AI uses **semantic retrieval**, allowing it to identify relevant content based on the meaning of the student's question.

For example:

**Question:**

> *"How does regularization help prevent a model from overfitting?"*

Even if the exact wording does not appear in the document, the system can retrieve sections discussing regularization, model complexity, and overfitting based on their semantic relationship.

This makes the interaction more natural than traditional keyword-based document search.

---

## 🔎 Transparent AI Responses

StudyMate AI also allows users to inspect the **retrieved document content** behind an answer.

This provides better visibility into where the information came from and helps students verify the generated response against their original study material.

---

## 🚀 Future Enhancements

Planned improvements include:

- 📚 Multiple document support
- 📑 Page-level citations
- 📝 Automatic quiz generation
- 🃏 AI-generated flashcards
- 📊 Study progress tracking
- 🎤 Voice-based interaction
- 🌐 Support for additional document formats
- 🧠 Improved conversational memory
- ⚡ Streaming AI responses
- 🔐 User authentication
- ☁️ Cloud deployment

---

## ▶️ Getting Started

### Prerequisites

- Python 3.14+
- OpenAI API key

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/StudyMateAI.git
cd StudyMateAI
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file and add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key
```

### Run the Application

```bash
streamlit run app.py
```

The StudyMate AI interface will open in your browser.

---

## 👩‍💻 Author

### Bhoomika Somavarapu

MSc Artificial Intelligence Student

**Interested in:** Artificial Intelligence · Generative AI · RAG · LLM Applications · Machine Learning

⭐ **If you find StudyMate AI interesting, consider giving the repository a star!**
