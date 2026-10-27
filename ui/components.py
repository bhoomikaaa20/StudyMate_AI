from html import escape
from pathlib import Path

import streamlit as st


GITHUB_URL = "https://github.com/bhoomikaaa20/StudyMate_AI"

STYLES_PATH = Path(__file__).parent / "styles.css"

LOGO_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M4 19.5V5a2 2 0 0 1 2-2h12v15H6.5A2.5 2.5 0 0 0 4 20.5"/>'
    '<path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H18v-5"/>'
    '<path d="M11 7l1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/>'
    '</svg>'
)


def _render(markup):

    # Collapse indentation so Markdown never treats HTML as a code block
    st.markdown(
        " ".join(line.strip() for line in markup.splitlines()),
        unsafe_allow_html=True
    )


# =========================================================
# GLOBAL STYLES
# =========================================================

def load_styles():

    st.html(
        f"<style>{STYLES_PATH.read_text(encoding='utf-8')}</style>"
    )


# =========================================================
# LOADING SCREEN
# =========================================================

def loading_screen():

    return (
        '<div class="sm-boot">'
        f'<div class="sm-boot-logo">{LOGO_SVG}</div>'
        '<div class="sm-boot-title">StudyMate AI</div>'
        '<div class="sm-boot-sub">Loading AI models and your knowledge base…</div>'
        '<div class="sm-boot-bar"><span></span></div>'
        '</div>'
    )


# =========================================================
# NAVBAR + HERO
# =========================================================

def navbar(vector_count):

    status = (
        "Knowledge base ready"
        if vector_count
        else "Waiting for documents"
    )

    _render(f"""
        <nav class="sm-nav">
            <a class="sm-brand" href="#">
                <div class="sm-logo">{LOGO_SVG}</div>
                <div>
                    <div class="sm-brand-name">StudyMate AI</div>
                    <div class="sm-brand-tag">Your AI study companion</div>
                </div>
            </a>
            <div class="sm-nav-links">
                <a class="sm-nav-link active" href="#workspace">Workspace</a>
                <a class="sm-nav-link" href="#how-it-works">How it works</a>
                <a class="sm-nav-link" href="{GITHUB_URL}" target="_blank">GitHub ↗</a>
                <span class="sm-status"><span class="sm-dot"></span>{status}</span>
            </div>
        </nav>
    """)


def hero():

    chips = [
        "LangChain", "OpenAI GPT-5 nano", "ChromaDB",
        "text-embedding-3-small", "MMR Retrieval", "Streamlit"
    ]

    chip_html = "".join(
        f'<span class="sm-chip">{c}</span>' for c in chips
    )

    _render(f"""
        <section class="sm-hero" id="workspace">
            <div>
                <div class="sm-eyebrow">✦ Retrieval-Augmented Generation</div>
                <h1>Chat with your <span class="sm-gradient-text">study material</span>.</h1>
                <p>Upload any PDF — lecture notes, research papers, textbooks — and get
                grounded answers with the exact passages they came from.</p>
            </div>
            <div class="sm-tech">{chip_html}</div>
        </section>
    """)


# =========================================================
# STATS
# =========================================================

def stats(vector_count, documents, questions):

    cards = [
        ("🧩", "#EEECFF", "Indexed chunks", f"{vector_count:,}", ""),
        ("📄", "#E0F2FE", "Documents this session", f"{documents}", ""),
        ("💬", "#FCE7F3", "Questions asked", f"{questions}", ""),
        ("🎯", "#E7F8F1", "Retrieval strategy", "MMR", "k=3"),
    ]

    html = "".join(
        f"""
        <div class="sm-stat">
            <div class="sm-stat-icon" style="background:{bg}">{icon}</div>
            <div>
                <div class="sm-stat-label">{label}</div>
                <div class="sm-stat-value">{value}<small>{suffix}</small></div>
            </div>
        </div>
        """
        for icon, bg, label, value, suffix in cards
    )

    _render(f'<div class="sm-stats">{html}</div>')


# =========================================================
# CARDS
# =========================================================

def card_header(icon, title, subtitle=None, pill=None):

    pill_html = f'<span class="sm-pill">{pill}</span>' if pill else ""

    sub_html = (
        f'<div class="sm-card-sub">{subtitle}</div>' if subtitle else ""
    )

    _render(f"""
        <div class="sm-card-head">
            <div class="sm-card-title"><span class="sm-ico">{icon}</span>{title}</div>
            {pill_html}
        </div>
        {sub_html}
    """)


def process_result(file_name, pages, chunks, total_vectors):

    _render(f"""
        <div class="sm-result">
            <div class="sm-result-title">✓ {escape(file_name)} indexed successfully</div>
            <div class="sm-result-grid">
                <div><b>{pages}</b><span>Pages</span></div>
                <div><b>{chunks}</b><span>Chunks</span></div>
                <div><b>{total_vectors:,}</b><span>Total vectors</span></div>
            </div>
        </div>
    """)


def pipeline_steps():

    steps = [
        ("Upload", "Drop a PDF — it's hashed (MD5) so duplicates are never re-indexed."),
        ("Chunk", "Pages are split into 500-character chunks with 50-character overlap."),
        ("Embed & store", "Chunks are embedded with OpenAI and persisted in ChromaDB."),
        ("Retrieve", "MMR search picks the 3 most relevant yet diverse chunks."),
        ("Answer", "GPT-5 nano answers strictly from the retrieved context."),
    ]

    html = "".join(
        f"""
        <div class="sm-step">
            <div class="sm-step-num">{i}</div>
            <div><b>{title}</b><span>{desc}</span></div>
        </div>
        """
        for i, (title, desc) in enumerate(steps, start=1)
    )

    _render(f'<div class="sm-steps" id="how-it-works">{html}</div>')


# =========================================================
# CHAT
# =========================================================

def empty_state():

    _render(f"""
        <div class="sm-empty">
            <div class="sm-empty-icon">{LOGO_SVG}</div>
            <h3>What would you like to learn today?</h3>
            <p>Ask anything about your indexed documents. Every answer is grounded
            in your material — with sources you can inspect.</p>
            <div class="sm-suggest-label">Try asking</div>
        </div>
    """)


def sources(docs):

    for i, doc in enumerate(docs, start=1):

        page = doc.get("page")

        page_html = f" · p. {page + 1}" if isinstance(page, int) else ""

        # Keep line breaks and stop "$" from being parsed as LaTeX
        content = (
            escape(doc["content"])
            .replace("$", "&#36;")
            .replace("\n", "<br>")
        )

        _render(f"""
            <div class="sm-source">
                <div class="sm-source-head">
                    <span>Chunk {i}</span>
                    <span>{escape(str(doc.get("source", "Unknown")))}{page_html}</span>
                </div>
                <div class="sm-source-body">{content}</div>
            </div>
        """)


def thinking():

    return (
        '<div style="color:#8A93A6;font-size:.88rem;">'
        '✦ Reading your documents and composing an answer…</div>'
    )


def footer():

    _render(f"""
        <footer class="sm-footer">
            <span>StudyMate AI · Built with LangChain, ChromaDB, OpenAI & Streamlit</span>
            <a href="{GITHUB_URL}" target="_blank">View source on GitHub ↗</a>
        </footer>
    """)
