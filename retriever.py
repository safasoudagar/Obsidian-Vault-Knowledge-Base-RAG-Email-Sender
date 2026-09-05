import chromadb
from sentence_transformers import SentenceTransformer
from generator import generate_answer


# Load the same embedding model used during indexing
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Distance threshold for relevance
RELEVANCE_THRESHOLD = 1.2


def get_collection(db_path="chroma_db"):
    """
    Connect to the ChromaDB created for a specific vault.
    """

    client = chromadb.PersistentClient(
        path=db_path
    )

    return client.get_collection(
        name="obsidian_notes"
    )


def search_notes(
    query,
    db_path="chroma_db",
    top_k=5
):
    """
    Search the vector database and keep only
    sufficiently relevant chunks.
    """

    collection = get_collection(
        db_path
    )

    # Convert question into an embedding
    query_embedding = embedding_model.encode(
        [query]
    )

    # Retrieve candidate chunks
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k
    )

    # Store only relevant chunks
    relevant_chunks = []

    for i in range(
        len(results["documents"][0])
    ):

        distance = results["distances"][0][i]

        if distance <= RELEVANCE_THRESHOLD:

            metadata = results[
                "metadatas"
            ][0][i]

            relevant_chunks.append({
                "text": results[
                    "documents"
                ][0][i],

                "source": metadata[
                    "source"
                ],

                "path": metadata[
                    "path"
                ],

                "heading_path": metadata[
                    "heading_path"
                ],

                "distance": distance
            })

    return relevant_chunks


if __name__ == "__main__":

    question = input(
        "\nAsk a question: "
    ).strip()

    if not question:

        print(
            "Please enter a question."
        )

        exit()

    # Retrieve relevant notes
    retrieved_chunks = search_notes(
        question,
        db_path="chroma_db",
        top_k=5
    )

    print(
        "\nRetrieved relevant information:\n"
    )

    if not retrieved_chunks:

        print(
            "No relevant information found."
        )

        print(
            "\n" + "=" * 60
        )

        print("ANSWER")

        print(
            "=" * 60
        )

        print(
            "I couldn't find this information "
            "in your Obsidian notes."
        )

        exit()

    for i, chunk in enumerate(
        retrieved_chunks
    ):

        print(
            "=" * 60
        )

        print(
            f"Result {i + 1}"
        )

        print(
            "Source:",
            chunk["source"]
        )

        print(
            "Section:",
            chunk["heading_path"]
        )

        print(
            "Distance:",
            chunk["distance"]
        )

        print(
            "-" * 60
        )

        print(
            chunk["text"]
        )

    print(
        "\nGenerating answer...\n"
    )

    # Send ONLY relevant chunks to Qwen3
    answer = generate_answer(
        question,
        retrieved_chunks
    )

    print(
        "=" * 60
    )

    print("ANSWER")

    print(
        "=" * 60
    )

    print(answer)

    print(
        "\n" + "=" * 60
    )

    print("SOURCES")

    print(
        "=" * 60
    )

    for chunk in retrieved_chunks:

        print(
            f"- {chunk['source']} "
            f"→ {chunk['heading_path']}"
        )