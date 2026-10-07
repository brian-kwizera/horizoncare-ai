from pathlib import Path

from database import get_connection


SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def initialize_database() -> None:
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)

        connection.commit()