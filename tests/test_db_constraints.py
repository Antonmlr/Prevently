# ============================================================
#  test_db_constraints.py -- "Database" part of the test plan.
#
#  Requirement:
#  "A record that violates a constraint (e.g. a checkup with
#  age_min > age_max, or a missing required field) is rejected
#  by the API (4xx)." -- here checked one level below the API,
#  directly against the constraints Postgres enforces.
# ============================================================
import psycopg2.errors
import pytest


def test_user_rejects_unknown_insurance_id(db_conn):
    """FK: prevently_user.insurance_id -> insurance_provider."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cur.execute(
            """INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender, insurance_id)
               VALUES ('A', 'B', '2000-01-01', 'Male', 999999)"""
        )
    db_conn.rollback()


def test_user_rejects_missing_required_field(db_conn, seed_insurance):
    """NOT NULL: first_name is required."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.NotNullViolation):
        cur.execute(
            """INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender, insurance_id)
               VALUES (NULL, 'B', '2000-01-01', 'Male', %s)""",
            (seed_insurance,),
        )
    db_conn.rollback()


def test_checkup_rejects_age_max_below_age_min(db_conn):
    """CHECK (age_max > age_min)."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.CheckViolation):
        cur.execute(
            """INSERT INTO checkup (title, age_min, age_max, required_gender)
               VALUES ('Invalid', 50, 20, 'Any')"""
        )
    db_conn.rollback()


def test_checkup_rejects_negative_age_min(db_conn):
    """CHECK (age_min >= 0)."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.CheckViolation):
        cur.execute(
            """INSERT INTO checkup (title, age_min, age_max, required_gender)
               VALUES ('Invalid', -1, 20, 'Any')"""
        )
    db_conn.rollback()


def test_completed_checkup_rejects_unknown_user(db_conn, seed_doctor, seed_checkup):
    """FK: completed_checkup.user_id -> prevently_user."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cur.execute(
            """INSERT INTO completed_checkup (user_id, doctor_id, checkup_id, completed_date)
               VALUES (999999, %s, %s, current_date)""",
            (seed_doctor, seed_checkup),
        )
    db_conn.rollback()


def test_appointment_rejects_unknown_doctor(db_conn, seed_user, seed_checkup):
    """FK: appointment.doctor_id -> doctor."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cur.execute(
            """INSERT INTO appointment (user_id, doctor_id, checkup_id, checkup_date, duration)
               VALUES (%s, 999999, %s, current_date, 30)""",
            (seed_user, seed_checkup),
        )
    db_conn.rollback()


def test_appointment_rejects_unknown_checkup(db_conn, seed_user, seed_doctor):
    """FK: appointment.checkup_id -> checkup."""
    cur = db_conn.cursor()
    with pytest.raises(psycopg2.errors.ForeignKeyViolation):
        cur.execute(
            """INSERT INTO appointment (user_id, doctor_id, checkup_id, checkup_date, duration)
               VALUES (%s, %s, 999999, current_date, 30)""",
            (seed_user, seed_doctor),
        )
    db_conn.rollback()
