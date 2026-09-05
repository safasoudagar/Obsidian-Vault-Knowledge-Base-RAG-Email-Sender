from pathlib import Path


# Default vault used for testing
DEFAULT_VAULT_PATH = Path("vault")


def load_markdown_files(vault_path=DEFAULT_VAULT_PATH):
    """
    Load all Markdown files from the specified vault.

    Parameters:
        vault_path: Path to an Obsidian vault.

    Returns:
        A list of dictionaries containing note text,
        source filename, and full file path.
    """

    vault_path = Path(vault_path)

    # Check that the vault exists
    if not vault_path.exists():
        raise FileNotFoundError(
            f"Vault not found: {vault_path}"
        )

    # Check that the path is actually a directory
    if not vault_path.is_dir():
        raise NotADirectoryError(
            f"Vault path is not a directory: {vault_path}"
        )

    documents = []

    # Find every Markdown file inside the vault,
    # including files inside subfolders.
    for file_path in vault_path.rglob("*.md"):

        # Ignore Obsidian's internal configuration folder
        if ".obsidian" in file_path.parts:
            continue

        # Read the Markdown file
        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "text": content,
            "source": file_path.name,
            "path": str(file_path)
        })

    return documents


if __name__ == "__main__":

    # Use the default test vault
    documents = load_markdown_files()

    print(f"Found {len(documents)} Markdown files.\n")

    for document in documents:

        print("=" * 50)
        print(f"Source: {document['source']}")
        print("=" * 50)
        print(document["text"])
        print()