import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"

load_dotenv(ENV_FILE)

test_database_url = os.getenv("TEST_DATABASE_URL")

if not test_database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL is missing from backend/.env"
    )

database_name = urlsplit(test_database_url).path.lstrip("/")

if database_name != "horizoncare_test":
    raise RuntimeError(
        "Tests must use the horizoncare_test database."
    )

# Ensure application database connections during pytest use the test DB.
os.environ["DATABASE_URL"] = test_database_url


def clear_test_data() -> None:
    """Clear knowledge records without deleting the schema or extension."""
    from database import get_connection

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            actual_database = cursor.fetchone()[0]

            if actual_database != "horizoncare_test":
                raise RuntimeError(
                    "Refusing to clear data outside horizoncare_test."
                )

            cursor.execute(
                """
                TRUNCATE TABLE
                    document_chunks,
                    documents
                RESTART IDENTITY CASCADE;
                """
            )


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    from database_setup import initialize_database

    initialize_database()
    clear_test_data()

    yield

    clear_test_data()


@pytest.fixture(autouse=True)
def isolate_each_test(prepare_test_database):
    clear_test_data()

    yield

    clear_test_data()