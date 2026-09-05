# Obsidian Knowledge Base + RAG Email Assistant

An AI-powered knowledge assistant that uses an Obsidian Markdown vault as a private knowledge base.

The system uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from the user's notes and generate answers using a local LLM. Answers can also be sent directly to an email address.

## Features

- Upload an Obsidian vault as a ZIP file
- Automatically discover Markdown notes
- Hierarchical Markdown chunking using headings
- Generate embeddings using Sentence Transformers
- Store embeddings in ChromaDB
- Semantic search over notes
- RAG-based question answering
- Local Qwen3 LLM using Ollama
- Source citations for retrieved notes
- Email answers using Gmail SMTP
- Streamlit web interface

## Architecture

Obsidian Vault (.md)
        ↓
Markdown Ingestion
        ↓
Hierarchical Chunking
        ↓
Sentence Transformer Embeddings
        ↓
ChromaDB Vector Database
        ↓
Query Embedding
        ↓
Semantic Retrieval
        ↓
Qwen3 RAG Generation
        ↓
Answer + Sources
        ↓
Optional Email


## Project Structure
obsidian-rag/
│
├── app.py
├── ingestion.py
├── chunking.py
├── embeddings.py
├── vectorstore.py
├── retriever.py
├── generator.py
├── vault_manager.py
├── email_sender.py
│
├── vault/
│   ├── Machine Learning.md
│   ├── Computer Networks.md
│   └── Python.md
│
├── .gitignore
└── README.md

## How RAG Works
1.Markdown files are loaded from the Obsidian vault.
2.Notes are divided into hierarchical chunks based on Markdown headings.
3.Each chunk is converted into a vector embedding.
4.Embeddings are stored in ChromaDB.
5.When a user asks a question, the question is converted into an embedding.
6.ChromaDB retrieves the most relevant note chunks.
7.The retrieved context is provided to the Qwen3 local LLM.
8.The LLM generates an answer using only the retrieved information.
9.The application displays the answer along with its source notes.
10.The answer can optionally be sent by email.

## Requirements

Before running the application, make sure you have:

- Python 3.12
- Ollama
- Qwen3 1.7B model
- An Obsidian vault containing Markdown (`.md`) notes
- Gmail account with 2-Step Verification and an App Password (only if using email functionality)

The uploaded Obsidian vault must be provided as a `.zip` file.

The vault should contain Markdown (`.md`) files.

Example:

my-vault.zip
└── My Obsidian Vault/
    ├── Machine Learning.md
    ├── Python.md
    └── Computer Networks.md

## Installation

Clone the repository:

git clone <your-github-repository-url>

Navigate to the project:

cd obsidian-rag

Create and activate the Conda environment:

conda create -n obsidian-rag python=3.12
conda activate obsidian-rag

Install dependencies:

pip install streamlit sentence-transformers chromadb python-dotenv ollama

Download the Qwen3 model:

ollama pull qwen3:1.7b

## Email Configuration

Create a `.env` file in the project root:

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

For Gmail, use a Google App Password instead of your normal Gmail password.

Never commit the `.env` file to GitHub.

## How to Use

Start the application:

streamlit run app.py

The Streamlit interface will open in your browser.

### Step 1: Upload an Obsidian Vault

Upload your Obsidian vault as a `.zip` file.

The ZIP file should contain Markdown (`.md`) notes.

The application automatically searches the uploaded vault for Markdown files.

### Step 2: Index the Vault

Click **Index Vault**.

The application will:

1. Read the Markdown files.
2. Split the notes into hierarchical chunks using Markdown headings.
3. Generate embeddings using `all-MiniLM-L6-v2`.
4. Store the embeddings in ChromaDB.

### Step 3: Ask a Question

Enter a question related to your notes.

For example:

"What is supervised learning?"

The system retrieves the most relevant chunks from the vault and provides them to the Qwen3 model as context.

### Step 4: View the Answer and Sources

The generated answer is displayed along with the source note and section from which the information was retrieved.

If the information cannot be found in the notes, the application responds:

"I couldn't find this information in your Obsidian notes."

### Step 5: Send the Answer by Email

Enter the recipient's email address and click **Send Answer**.

The email contains:

- The question
- The generated answer
- The source notes and sections

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Vector database |
| Ollama | Local LLM runtime |
| Qwen3 1.7B | RAG answer generation |
| Gmail SMTP | Email delivery |

## Important Notes

- The application currently runs the Qwen3 model locally through Ollama.
- Answer generation may take a few seconds. Please be patient and wait for the response to finish generating.
- The uploaded vault must be provided as a ZIP file.
- The vault should contain Markdown (`.md`) files.
- `.env` contains sensitive email credentials and must not be committed.
- The application ignores the `.obsidian` directory when processing vault files.

