from sentence_transformers import SentenceTransformer
from ingestion import load_markdown_files


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(texts):
    """
    Convert a list of texts into numerical vectors.
    """
    return model.encode(texts)


if __name__ == "__main__":

    # Read all Markdown files from the vault
    documents = load_markdown_files()

    # Extract the text from each document
    texts = [document["text"] for document in documents]

    # Create embeddings
    vectors = create_embeddings(texts)

    print("Number of documents:", len(documents))
    print("Vector shape:", vectors.shape)

    # Show which file each vector belongs to
    for i, document in enumerate(documents):
        print(f"{i + 1}. {document['source']}")