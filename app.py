import streamlit as st
from pathlib import Path
import tempfile

from vault_manager import (
    get_sample_vault,
    extract_vault_zip,
    find_markdown_files
)
from vectorstore import create_vectorstore
from retriever import search_notes
from generator import generate_answer
from email_sender import send_email


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Obsidian RAG Assistant",
    page_icon="🧠",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    /* ---------- Main Background ---------- */

    .stApp {
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #172554 50%,
            #1e1b4b 100%
        );
    }


    /* ---------- Sidebar ---------- */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827 0%,
            #1e1b4b 100%
        );
        border-right: 1px solid #4f46e5;
    }


    /* ---------- Main Title ---------- */

    .main-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(
            90deg,
            #a78bfa,
            #60a5fa,
            #22d3ee
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }


    .subtitle {
        font-size: 18px;
        color: #cbd5e1;
        margin-bottom: 30px;
    }


    /* ---------- Section Titles ---------- */

    .section-title {
        font-size: 28px;
        font-weight: 700;
        color: #e0e7ff;
        margin-top: 25px;
        margin-bottom: 15px;
    }


    /* ---------- Information Cards ---------- */

    .info-card {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(96, 165, 250, 0.35);
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 20px;
    }


    .answer-card {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.35);
        border-radius: 15px;
        padding: 20px;
        margin-top: 10px;
    }


    .source-card {
        background: rgba(139, 92, 246, 0.12);
        border: 1px solid rgba(167, 139, 250, 0.35);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 8px 0;
    }


    .email-card {
        background: rgba(236, 72, 153, 0.12);
        border: 1px solid rgba(244, 114, 182, 0.35);
        border-radius: 15px;
        padding: 20px;
        margin-top: 25px;
    }


    /* ---------- Buttons ---------- */

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #6366f1;
        background: linear-gradient(
            90deg,
            #4f46e5,
            #7c3aed
        );
        color: white;
        font-weight: 600;
        transition: 0.2s;
    }


    .stButton > button:hover {
        border-color: #a78bfa;
        transform: translateY(-1px);
    }


    /* ---------- Text Input ---------- */

    div[data-baseweb="input"] {
        border-radius: 10px;
    }


    /* ---------- Sidebar Text ---------- */

    [data-testid="stSidebar"] p {
        color: #cbd5e1;
    }


    /* ---------- Divider ---------- */

    hr {
        border-color: rgba(148, 163, 184, 0.25);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================

if "vault_path" not in st.session_state:
    st.session_state.vault_path = None

if "db_path" not in st.session_state:
    st.session_state.db_path = None

if "indexed" not in st.session_state:
    st.session_state.indexed = False

if "uploaded_temp_dir" not in st.session_state:
    st.session_state.uploaded_temp_dir = None

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">🧠 Obsidian RAG Knowledge Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions about your Obsidian notes using '
    '<b>Retrieval-Augmented Generation (RAG)</b>.'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.markdown("## 📚 Knowledge Source")

vault_option = st.sidebar.radio(
    "Choose your vault:",
    ["Sample Vault", "Upload Obsidian Vault"]
)


# ==================================================
# SAMPLE VAULT
# ==================================================

if vault_option == "Sample Vault":

    st.sidebar.info(
        "Use the built-in sample notes to test the RAG system."
    )

    if st.sidebar.button("📚 Use Sample Vault"):

        vault_path = get_sample_vault()

        session_dir = Path(
            tempfile.mkdtemp(
                prefix="obsidian_rag_session_"
            )
        )

        db_path = session_dir / "chroma_db"

        st.session_state.vault_path = vault_path
        st.session_state.db_path = db_path
        st.session_state.indexed = False
        st.session_state.uploaded_temp_dir = None

        st.session_state.last_answer = None
        st.session_state.last_sources = []

        st.sidebar.success("Sample vault selected.")


# ==================================================
# UPLOAD VAULT
# ==================================================

else:

    st.sidebar.info(
        "Zip your Obsidian vault and upload the ZIP file here."
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload Obsidian Vault",
        type=["zip"]
    )

    if uploaded_file is not None:

        if st.sidebar.button("📁 Load Uploaded Vault"):

            try:

                temp_zip = Path(
                    tempfile.mktemp(
                        suffix=".zip"
                    )
                )

                with open(temp_zip, "wb") as f:
                    f.write(
                        uploaded_file.getbuffer()
                    )

                extracted_vault = extract_vault_zip(
                    temp_zip
                )

                session_dir = Path(
                    tempfile.mkdtemp(
                        prefix="obsidian_rag_session_"
                    )
                )

                db_path = session_dir / "chroma_db"

                st.session_state.vault_path = extracted_vault
                st.session_state.db_path = db_path
                st.session_state.indexed = False
                st.session_state.uploaded_temp_dir = extracted_vault

                st.session_state.last_answer = None
                st.session_state.last_sources = []

                temp_zip.unlink(
                    missing_ok=True
                )

                st.sidebar.success(
                    "Vault loaded successfully."
                )

            except Exception as e:

                st.sidebar.error(
                    f"Error loading vault: {e}"
                )


# ==================================================
# SHOW AVAILABLE NOTES
# ==================================================

st.sidebar.divider()

if st.session_state.vault_path is not None:

    markdown_files = find_markdown_files(
        st.session_state.vault_path
    )

    st.sidebar.markdown(
        f"### 📝 Notes in vault: {len(markdown_files)}"
    )

    for file_path in markdown_files:

        st.sidebar.write(
            f"📄 {file_path.name}"
        )


    # ==================================================
    # INDEX VAULT
    # ==================================================

    if st.sidebar.button("🔨 Index Vault"):

        try:

            with st.spinner(
                "Reading and indexing notes..."
            ):

                create_vectorstore(
                    vault_path=st.session_state.vault_path,
                    db_path=st.session_state.db_path
                )

            st.session_state.indexed = True
            st.session_state.last_answer = None
            st.session_state.last_sources = []

            st.sidebar.success(
                "Vault indexed successfully!"
            )

        except Exception as e:

            st.sidebar.error(
                f"Indexing failed: {e}"
            )


# ==================================================
# ASK YOUR NOTES
# ==================================================

st.markdown(
    '<div class="section-title">💬 Ask Your Notes</div>',
    unsafe_allow_html=True
)


if not st.session_state.indexed:

    st.markdown(
        """
        <div class="info-card">
        📚 Select a vault and click <b>Index Vault</b>
        to start asking questions about your notes.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    question = st.text_input(
        "Ask a question about your notes:",
        placeholder="Example: What is supervised learning?"
    )

    if st.button("🔍 Ask"):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            # ------------------------------------------
            # RETRIEVAL
            # ------------------------------------------

            with st.spinner(
                "Searching your notes..."
            ):

                retrieved_chunks = search_notes(
                    question,
                    db_path=st.session_state.db_path,
                    top_k=5
                )


            # ------------------------------------------
            # NO RELEVANT INFORMATION
            # ------------------------------------------

            if not retrieved_chunks:

                st.session_state.last_answer = (
                    "I couldn't find this information "
                    "in your Obsidian notes."
                )

                st.session_state.last_sources = []


            # ------------------------------------------
            # GENERATE ANSWER
            # ------------------------------------------

            else:

                with st.spinner(
                    "Generating answer..."
                ):

                    answer = generate_answer(
                        question,
                        retrieved_chunks
                    )

                st.session_state.last_answer = answer
                st.session_state.last_sources = retrieved_chunks


# ==================================================
# DISPLAY ANSWER
# ==================================================

if st.session_state.last_answer is not None:

    st.markdown(
        '<div class="section-title">🤖 Answer</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="answer-card">
        {st.session_state.last_answer}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ==================================================
    # SOURCES
    # ==================================================

    if st.session_state.last_sources:

        st.markdown(
            '<div class="section-title">📄 Retrieved Sources</div>',
            unsafe_allow_html=True
        )

        for chunk in st.session_state.last_sources:

            st.markdown(
                f"""
                <div class="source-card">
                📄 <b>{chunk['source']}</b><br>
                📌 {chunk['heading_path']}
                </div>
                """,
                unsafe_allow_html=True
            )


        # ==================================================
        # EMAIL
        # ==================================================

        st.markdown("---")

        st.markdown(
            '<div class="section-title">📧 Send Answer to Email</div>',
            unsafe_allow_html=True
        )

        recipient_email = st.text_input(
            "Recipient email address:",
            placeholder="example@gmail.com"
        )


        if st.button("📧 Send Answer"):

            if not recipient_email.strip():

                st.warning(
                    "Please enter a recipient email address."
                )

            else:

                source_lines = []

                for chunk in st.session_state.last_sources:

                    source_lines.append(
                        f"- {chunk['source']} → "
                        f"{chunk['heading_path']}"
                    )

                sources_text = "\n".join(
                    source_lines
                )

                email_body = f"""Obsidian RAG Knowledge Assistant

Question:
{question}

Answer:
{st.session_state.last_answer}

Sources:
{sources_text}
"""


                try:

                    with st.spinner(
                        "Sending email..."
                    ):

                        send_email(
                            recipient_email.strip(),
                            "Obsidian RAG Answer",
                            email_body
                        )

                    st.success(
                        "📧 Answer sent successfully!"
                    )

                except Exception as e:

                    st.error(
                        f"Failed to send email: {e}"
                    )