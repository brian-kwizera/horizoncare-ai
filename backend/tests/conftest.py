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
        "Automated tests must use the horizoncare_test database."
    )

# Force all test-process database connections to the test database.
os.environ["DATABASE_URL"] = test_database_url


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    # Import only after DATABASE_URL points to the test database.
    from database_setup import initialize_database

    initialize_database()