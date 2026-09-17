
import os

import psycopg2
import psycopg2.extras
import pytest

# Points at the postgres service from docker-compose.test.yml. (Now hardcoded)
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://vorlesung:geheim@localhost:1905/vorlesung",
)

# main.py reads DATABASE_URL and API_KEY at import time, so both
# have to be set *before* we import it.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("API_KEY", "test-key")

import main  # noqa: E402  (import after env vars are set on purpose)

from fastapi.testclient import TestClient  # noqa: E402

# Every table in db/01_schema.sql. 
ALL_TABLES = [
    "appointment",
    "completed_checkup",
    "included_checkup",
    "medical_checkup",
    "doctor",
    "checkup",
    "prevently_user",
    "insurance_provider",
]


@pytest.fixture
def db_conn():
    """A raw psycopg2 connection for tests that seed data or check
    constraints directly against the database."""
    conn = psycopg2.connect(TEST_DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def clean_tables():
    """Runs after every single test and empties all tables.

    This has to happen on its own, fresh connection: POST endpoints hit
    through `client` commit on *their own* connection inside main.py, so a
    rollback on the `db_conn` fixture's connection would not undo them.
    TRUNCATE is the one thing that reliably cleans up after both paths.
    """
    yield
    conn = psycopg2.connect(TEST_DATABASE_URL)
    cur = conn.cursor()
    cur.execute(f"TRUNCATE {', '.join(ALL_TABLES)} RESTART IDENTITY CASCADE")
    conn.commit()
    cur.close()
    conn.close()


@pytest.fixture
def client():
    """FastAPI TestClient wired to the app from api/main.py."""
    return TestClient(main.app)


@pytest.fixture
def api_key_header():
    return {"X-API-Key": os.environ["API_KEY"]}


# ---- Seed data fixtures --------------------------------------
# Small, composable fixtures for the rows a test needs. Each one inserts
# exactly one row and returns its id.

@pytest.fixture
def seed_insurance(db_conn):
    cur = db_conn.cursor()
    cur.execute(
        "INSERT INTO insurance_provider (i_name) VALUES ('Test AOK') RETURNING insurance_id"
    )
    insurance_id = cur.fetchone()["insurance_id"]
    db_conn.commit()
    cur.close()
    return insurance_id


@pytest.fixture
def seed_user(db_conn, seed_insurance):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender, insurance_id)
           VALUES ('Test', 'User', '1990-01-01', 'Male', %s) RETURNING user_id""",
        (seed_insurance,),
    )
    user_id = cur.fetchone()["user_id"]
    db_conn.commit()
    cur.close()
    return user_id


@pytest.fixture
def seed_checkup(db_conn):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO checkup (title, age_min, age_max, required_gender)
           VALUES ('Test-Checkup', 18, 99, 'Any') RETURNING checkup_id"""
    )
    checkup_id = cur.fetchone()["checkup_id"]
    db_conn.commit()
    cur.close()
    return checkup_id


@pytest.fixture
def seed_doctor(db_conn):
    cur = db_conn.cursor()
    cur.execute(
        "INSERT INTO doctor (d_name, location) VALUES ('Dr. Test', 'Bochum') RETURNING doctor_id"
    )
    doctor_id = cur.fetchone()["doctor_id"]
    db_conn.commit()
    cur.close()
    return doctor_id


@pytest.fixture
def seed_medical_checkup(db_conn, seed_doctor, seed_checkup):
    """Links seed_doctor to seed_checkup, so /checkups/{id}/doctors finds it."""
    cur = db_conn.cursor()
    cur.execute(
        "INSERT INTO medical_checkup (doctor_id, checkup_id) VALUES (%s, %s)",
        (seed_doctor, seed_checkup),
    )
    db_conn.commit()
    cur.close()
    return seed_doctor, seed_checkup
