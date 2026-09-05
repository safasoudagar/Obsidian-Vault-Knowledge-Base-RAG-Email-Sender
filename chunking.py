import re
from ingestion import load_markdown_files


def chunk_text(text):
    """
    Split Markdown text into chunks based on headings
    while preserving the heading hierarchy.
    """

    # Split whenever we encounter a Markdown heading
    sections = re.split(
        r"(?m)(?=^#{1,6}\s)",
        text
    )

    chunks = []

    # Keeps track of headings at different levels
    heading_stack = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        # Check whether this section starts with a heading
        heading_match = re.match(
            r"^(#{1,6})\s+(.+)",
            section
        )

        if heading_match:

            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()

            # Remove headings at the same or deeper level
            heading_stack = [
                item
                for item in heading_stack
                if item[0] < level
            ]

            # Add current heading
            heading_stack.append(
                (level, heading)
            )

            # Build hierarchy
            heading_path = " > ".join(
                item[1]
                for item in heading_stack
            )

        else:
            heading_path = " > ".join(
                item[1]
                for item in heading_stack
            )

        # Add hierarchy to the chunk
        chunk_text_with_context = (
            f"Section: {heading_path}\n\n"
            f"{section}"
        )

        chunks.append({
            "text": chunk_text_with_context,
            "heading_path": heading_path
        })

    return chunks


def create_chunks(vault_path="vault"):
    """
    Load Markdown files and create hierarchical chunks.

    Returns:
        A list of dictionaries containing:
        - text
        - source
        - path
        - heading_path
        - chunk_id
    """

    documents = load_markdown_files(vault_path)

    all_chunks = []

    for document in documents:

        chunks = chunk_text(
            document["text"]
        )

        for i, chunk in enumerate(chunks):

            all_chunks.append({
                "text": chunk["text"],
                "source": document["source"],
                "path": document["path"],
                "heading_path": chunk["heading_path"],
                "chunk_id": (
                    f"{document['source']}_{i}"
                )
            })

    return all_chunks


if __name__ == "__main__":

    all_chunks = create_chunks()

    print(
        "Number of chunks:",
        len(all_chunks)
    )

    print("\nChunks:\n")

    for i, chunk in enumerate(all_chunks):

        print("=" * 60)
        print(f"Chunk {i + 1}")
        print(f"Source: {chunk['source']}")
        print(
            f"Heading path: "
            f"{chunk['heading_path']}"
        )
        print("-" * 60)
        print(chunk["text"])