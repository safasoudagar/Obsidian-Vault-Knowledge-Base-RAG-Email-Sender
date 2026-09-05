import chromadb
from sentence_transformers import SentenceTransformer
from chunking import create_chunks


# Load embedding model
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def create_vectorstore(
    vault_path="vault",
    db_path="chroma_db"
):
    """
    Create a ChromaDB vector store for a specific vault.

    Parameters:
        vault_path: Path to the Markdown/Obsidian vault.
        db_path: Path where the ChromaDB database will be stored.

    Returns:
        ChromaDB collection.
    """

    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=db_path
    )

    # Delete the old collection so that
    # we rebuild the index using the latest chunks.
    try:
        client.delete_collection(
            "obsidian_notes"
        )
        print("Old collection deleted.")

    except Exception:
        pass

    # Create a fresh collection
    collection = client.create_collection(
        name="obsidian_notes"
    )

    # Read and chunk the vault
    all_chunks = create_chunks(
        vault_path
    )

    if not all_chunks:
        raise ValueError(
            "No Markdown files were found "
            "in the vault."
        )

    # Extract chunk text
    texts = [
        chunk["text"]
        for chunk in all_chunks
    ]

    # Generate embeddings
    embeddings = embedding_model.encode(
        texts
    )

    # Store chunks and metadata
    collection.add(
        ids=[
            chunk["chunk_id"]
            for chunk in all_chunks
        ],

        documents=texts,

        embeddings=embeddings.tolist(),

        metadatas=[
            {
                "source": chunk["source"],
                "path": chunk["path"],
                "heading_path": chunk[
                    "heading_path"
                ]
            }
            for chunk in all_chunks
        ]
    )

    print(
        f"Added {len(all_chunks)} "
        "chunks to ChromaDB."
    )

    return collection


if __name__ == "__main__":

    create_vectorstore(
        vault_path="vault",
        db_path="chroma_db"
    )