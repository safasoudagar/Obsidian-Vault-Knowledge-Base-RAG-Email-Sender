from pathlib import Path
import tempfile
import zipfile
import shutil


def find_markdown_files(vault_path):
    """
    Find all Markdown files inside an Obsidian vault.

    The .obsidian configuration folder is ignored.
    """

    vault_path = Path(vault_path)

    markdown_files = []

    for file_path in vault_path.rglob("*.md"):

        # Ignore Obsidian's internal configuration
        if ".obsidian" in file_path.parts:
            continue

        markdown_files.append(file_path)

    return markdown_files


def validate_zip(zip_path):
    """
    Validate an uploaded ZIP file before extraction.

    Reject unsafe paths such as absolute paths
    and path traversal using '..'.
    """

    with zipfile.ZipFile(zip_path, "r") as zip_file:

        for member in zip_file.infolist():

            member_path = Path(member.filename)

            # Prevent absolute paths
            if member_path.is_absolute():
                raise ValueError(
                    "Unsafe ZIP file: absolute path detected."
                )

            # Prevent path traversal
            if ".." in member_path.parts:
                raise ValueError(
                    "Unsafe ZIP file: path traversal detected."
                )

    return True


def extract_vault_zip(zip_path):
    """
    Safely extract an Obsidian vault ZIP into
    a temporary directory.

    Returns:
        Path to the extracted vault.
    """

    zip_path = Path(zip_path)

    if not zip_path.exists():
        raise FileNotFoundError(
            f"ZIP file not found: {zip_path}"
        )

    # Validate ZIP before extraction
    validate_zip(zip_path)

    # Create temporary workspace
    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="obsidian_rag_"
        )
    )

    # Extract ZIP
    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_file:

        zip_file.extractall(temp_dir)

    # Find Markdown files
    markdown_files = find_markdown_files(
        temp_dir
    )

    if not markdown_files:

        # Clean up if no notes were found
        shutil.rmtree(
            temp_dir,
            ignore_errors=True
        )

        raise ValueError(
            "No Markdown files were found "
            "in the uploaded vault."
        )

    return temp_dir


def get_sample_vault():
    """
    Return the path to the sample vault.
    """

    sample_vault = Path("vault")

    if not sample_vault.exists():
        raise FileNotFoundError(
            "Sample vault was not found."
        )

    return sample_vault