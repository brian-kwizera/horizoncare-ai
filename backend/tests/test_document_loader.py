import pytest
from document_loader import (
    KnowledgeMetadataError,
    load_documents,
    parse_frontmatter,
    validate_metadata,
)


def test_load_documents():
    documents = load_documents()

    assert len(documents) >= 2

    documents_by_filename = {
        document["filename"]: document
        for document in documents
    }

    assert "malaria.md" in documents_by_filename
    assert "dengue.md" in documents_by_filename

    assert documents_by_filename["malaria.md"]["content"]
    assert documents_by_filename["dengue.md"]["content"]

    # Verify that metadata was parsed and frontmatter was removed from content
    malaria_doc = documents_by_filename["malaria.md"]
    assert "metadata" in malaria_doc
    assert malaria_doc["metadata"]["title"] == "Malaria"
    assert malaria_doc["metadata"]["publisher"] == "World Health Organization"
    assert not malaria_doc["content"].startswith("---")


def test_parse_frontmatter_valid():
    raw_text = """---
title: "Clinical Guidelines"
publisher: "Rwanda Ministry of Health"
source_url: "https://moh.gov.rw/guidelines"
publication_year: 2022
topics:
  - "Primary Care"
  - "Pediatrics"
---
# Clinical Guidelines Header

This is the actual clinical text.
"""
    metadata, content = parse_frontmatter(raw_text, filename="test.md")

    assert metadata["title"] == "Clinical Guidelines"
    assert metadata["publisher"] == "Rwanda Ministry of Health"
    assert metadata["source_url"] == "https://moh.gov.rw/guidelines"
    assert metadata["publication_year"] == 2022
    assert metadata["topics"] == ["Primary Care", "Pediatrics"]

    assert content.startswith("# Clinical Guidelines Header")
    assert "This is the actual clinical text." in content
    assert "---" not in content


def test_parse_frontmatter_missing_delimiters():
    raw_text = "Just plain text without any YAML frontmatter."
    with pytest.raises(KnowledgeMetadataError) as exc_info:
        parse_frontmatter(raw_text, filename="plain.md")

    assert "missing valid YAML frontmatter delimiters" in str(exc_info.value)


def test_parse_frontmatter_invalid_yaml():
    raw_text = """---
title: [unclosed list
publisher: "WHO"
---
Body text
"""
    with pytest.raises(KnowledgeMetadataError) as exc_info:
        parse_frontmatter(raw_text, filename="bad_yaml.md")

    assert "invalid YAML frontmatter" in str(exc_info.value)


@pytest.mark.parametrize(
    "missing_field",
    ["title", "publisher", "source_url", "publication_year", "topics"],
)
def test_parse_frontmatter_missing_required_fields(missing_field):
    metadata = {
        "title": "Title",
        "publisher": "Publisher",
        "source_url": "https://example.com",
        "publication_year": 2021,
        "topics": ["General"],
    }
    del metadata[missing_field]

    with pytest.raises(KnowledgeMetadataError) as exc_info:
        validate_metadata(metadata, filename="missing.md")

    assert f"missing required metadata field(s): {missing_field}" in str(exc_info.value)


def test_parse_frontmatter_invalid_field_types():
    # Invalid URL
    bad_url = {
        "title": "Title",
        "publisher": "Publisher",
        "source_url": "not-a-valid-url",
        "publication_year": 2021,
        "topics": ["Topic"],
    }
    with pytest.raises(KnowledgeMetadataError) as exc_info:
        validate_metadata(bad_url, filename="bad_url.md")
    assert "invalid 'source_url'" in str(exc_info.value)

    # Invalid Year (future year or out of range)
    bad_year = {
        "title": "Title",
        "publisher": "Publisher",
        "source_url": "https://example.com",
        "publication_year": 1850,
        "topics": ["Topic"],
    }
    with pytest.raises(KnowledgeMetadataError) as exc_info:
        validate_metadata(bad_year, filename="bad_year.md")
    assert "invalid 'publication_year'" in str(exc_info.value)

    # Empty topics
    empty_topics = {
        "title": "Title",
        "publisher": "Publisher",
        "source_url": "https://example.com",
        "publication_year": 2021,
        "topics": [],
    }
    with pytest.raises(KnowledgeMetadataError) as exc_info:
        validate_metadata(empty_topics, filename="bad_topics.md")
    assert "invalid 'topics'" in str(exc_info.value)


def test_load_documents_from_custom_directory(tmp_path):
    # Create valid document
    valid_file = tmp_path / "valid.md"
    valid_file.write_text(
        """---
title: "Custom Doc"
publisher: "WHO"
source_url: "https://example.com/custom"
publication_year: 2020
topics:
  - "Custom"
---
Custom content body
""",
        encoding="utf-8",
    )

    # Create a non-markdown file (should be ignored)
    ignore_file = tmp_path / "notes.txt"
    ignore_file.write_text("Should be ignored", encoding="utf-8")

    docs = load_documents(knowledge_dir=tmp_path)

    assert len(docs) == 1
    assert docs[0]["filename"] == "valid.md"
    assert docs[0]["metadata"]["title"] == "Custom Doc"
    assert docs[0]["content"] == "Custom content body"