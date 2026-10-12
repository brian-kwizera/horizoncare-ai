import re
from pathlib import Path
from typing import Any
import yaml


KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"


class KnowledgeMetadataError(ValueError):
    """Raised when knowledge document metadata is missing or invalid."""
    pass


def validate_metadata(metadata: Any, filename: str = "document.md") -> dict[str, Any]:
    """Validate that the parsed metadata complies with the required schema."""
    if not isinstance(metadata, dict):
        raise KnowledgeMetadataError(
            f"Metadata in '{filename}' must be a YAML mapping/dictionary."
        )

    required_fields = ["title", "publisher", "source_url", "publication_year", "topics"]
    missing = [field for field in required_fields if field not in metadata]
    if missing:
        raise KnowledgeMetadataError(
            f"Document '{filename}' is missing required metadata field(s): {', '.join(missing)}"
        )

    title = metadata.get("title")
    if not isinstance(title, str) or not title.strip():
        raise KnowledgeMetadataError(
            f"Document '{filename}' must have a non-empty string 'title'."
        )

    publisher = metadata.get("publisher")
    if not isinstance(publisher, str) or not publisher.strip():
        raise KnowledgeMetadataError(
            f"Document '{filename}' must have a non-empty string 'publisher'."
        )

    source_url = metadata.get("source_url")
    if not isinstance(source_url, str) or not (
        source_url.startswith("http://") or source_url.startswith("https://")
    ):
        raise KnowledgeMetadataError(
            f"Document '{filename}' has invalid 'source_url': must begin with http:// or https://."
        )

    pub_year = metadata.get("publication_year")
    if pub_year is not None:
        if not isinstance(pub_year, int) or isinstance(pub_year, bool) or pub_year < 1900 or pub_year > 2050:
            raise KnowledgeMetadataError(
                f"Document '{filename}' has invalid 'publication_year': must be an integer year between 1900 and 2050 (or null if unverified)."
            )

    topics = metadata.get("topics")
    if not isinstance(topics, list) or len(topics) == 0 or not all(isinstance(t, str) and t.strip() for t in topics):
        raise KnowledgeMetadataError(
            f"Document '{filename}' has invalid 'topics': must be a non-empty list of string tags."
        )

    return {
        "title": title.strip(),
        "publisher": publisher.strip(),
        "source_url": source_url.strip(),
        "publication_year": pub_year,
        "topics": [t.strip() for t in topics],
    }


def parse_frontmatter(text: str, filename: str = "document.md") -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter enclosed by triple-dash lines ('---').
    Returns (metadata_dict, clean_body_text).
    """
    pattern = r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?(.*)$"
    match = re.match(pattern, text, re.DOTALL)

    if not match:
        raise KnowledgeMetadataError(
            f"Document '{filename}' is missing valid YAML frontmatter delimiters ('---')."
        )

    raw_yaml, body = match.groups()

    try:
        parsed = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        raise KnowledgeMetadataError(
            f"Document '{filename}' has invalid YAML frontmatter: {exc}"
        ) from exc

    if parsed is None:
        raise KnowledgeMetadataError(
            f"Document '{filename}' frontmatter cannot be empty."
        )

    validated = validate_metadata(parsed, filename=filename)
    return validated, body.strip()


def load_documents(knowledge_dir: Path | None = None) -> list[dict[str, Any]]:
    directory = Path(knowledge_dir) if knowledge_dir is not None else KNOWLEDGE_DIR
    documents = []

    for file_path in sorted(directory.glob("*.md")):
        raw_text = file_path.read_text(encoding="utf-8")
        metadata, content = parse_frontmatter(raw_text, filename=file_path.name)
        documents.append(
            {
                "filename": file_path.name,
                "content": content,
                "metadata": metadata,
            }
        )

    return documents