from pathlib import Path


KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


def load_documents() -> list[dict]:
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        documents.append(
            {
                "filename": file_path.name,
                "content": file_path.read_text(encoding="utf-8"),
            }
        )

    return documents