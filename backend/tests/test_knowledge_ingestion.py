import pytest
from database import get_connection
from database_setup import initialize_database
from knowledge_ingestion import ingest_all_documents, ingest_document
import document_repository


def test_ingest_malaria_document():
    initialize_database()

    document_id = ingest_document(
        filename="malaria.md",
        title="Malaria",
        source="World Health Organization",
    )

    assert document_id > 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM document_chunks
                WHERE document_id = %s;
                """,
                (document_id,),
            )

            chunk_count = cursor.fetchone()[0]

    assert chunk_count > 0


def test_ingest_document_metadata_driven():
    """Verify document metadata is automatically resolved from YAML frontmatter."""
    initialize_database()

    # Ingest without providing title, source, or url explicitly
    document_id = ingest_document(filename="malaria.md")

    assert document_id > 0

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT filename, title, source, url
                FROM documents
                WHERE id = %s;
                """,
                (document_id,),
            )
            doc_row = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM document_chunks
                WHERE document_id = %s;
                """,
                (document_id,),
            )
            chunk_count = cursor.fetchone()[0]

    assert doc_row[0] == "malaria.md"
    assert doc_row[1] == "Malaria"
    assert doc_row[2] == "World Health Organization"
    assert doc_row[3] == "https://www.who.int/health-topics/malaria"
    assert chunk_count > 0


def test_repeat_ingestion_idempotency():
    """Verify repeat ingestion does not create duplicate documents or orphaned chunks."""
    initialize_database()

    # Ingest once
    doc_id_1 = ingest_document(filename="malaria.md")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM documents WHERE filename = %s;",
                ("malaria.md",),
            )
            doc_count_1 = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM document_chunks WHERE document_id = %s;",
                (doc_id_1,),
            )
            chunk_count_1 = cursor.fetchone()[0]

    # Ingest a second time
    doc_id_2 = ingest_document(filename="malaria.md")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM documents WHERE filename = %s;",
                ("malaria.md",),
            )
            doc_count_2 = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM document_chunks WHERE document_id = %s;",
                (doc_id_2,),
            )
            chunk_count_2 = cursor.fetchone()[0]

    assert doc_id_1 == doc_id_2
    assert doc_count_1 == 1
    assert doc_count_2 == 1
    assert chunk_count_1 == chunk_count_2


def test_ingest_document_rollback_on_failure(monkeypatch):
    """Verify transactional rollback: failed chunk insertion preserves prior working chunks."""
    initialize_database()

    # 1. Ingest successfully first
    document_id = ingest_document(filename="malaria.md")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM document_chunks WHERE document_id = %s;",
                (document_id,),
            )
            original_chunk_count = cursor.fetchone()[0]

    assert original_chunk_count > 0

    # 2. Simulate an error during chunk persistence inside save_document_and_chunks
    original_save = document_repository.save_document_and_chunks

    def faulty_save(*args, **kwargs):
        # Call original logic with invalid embedding syntax to force a database error
        chunks = args[4] if len(args) > 4 else kwargs.get("chunks", [])
        if chunks:
            chunks[0]["embedding"] = "invalid_vector_format"
        return original_save(*args, **kwargs)

    monkeypatch.setattr(document_repository, "save_document_and_chunks", faulty_save)

    with pytest.raises(Exception):
        ingest_document(filename="malaria.md")

    # 3. Verify original chunks were NOT deleted due to database rollback
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM document_chunks WHERE document_id = %s;",
                (document_id,),
            )
            retained_chunk_count = cursor.fetchone()[0]

    assert retained_chunk_count == original_chunk_count


def test_ingest_all_documents():
    """Verify automatic discovery and batch ingestion of all documents."""
    initialize_database()

    doc_ids = ingest_all_documents()

    assert len(doc_ids) >= 2

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT filename FROM documents ORDER BY filename;")
            rows = cursor.fetchall()

    filenames = [row[0] for row in rows]
    assert "malaria.md" in filenames
    assert "dengue.md" in filenames