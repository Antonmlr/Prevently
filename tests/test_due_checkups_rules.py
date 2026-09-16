# ============================================================
#  test_due_checkups_rules.py -- "Rules" part of the test plan.
#
#  Requirement: GET /users/{id}/due-checkups
#  must apply the JOIN + filter logic correctly.
#    1. A checkup the user already completed must not show up again.
#    2. A checkup outside the user's age/gender range must not appear.
# ============================================================
from datetime import date


def _make_user(db_conn, insurance_id, birth_year, gender):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender, insurance_id)
           VALUES ('Test', 'User', %s, %s, %s) RETURNING user_id""",
        (date(birth_year, 1, 1), gender, insurance_id),
    )
    user_id = cur.fetchone()["user_id"]
    db_conn.commit()
    return user_id


def _make_checkup(db_conn, title, age_min, age_max, required_gender):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO checkup (title, age_min, age_max, required_gender)
           VALUES (%s, %s, %s, %s) RETURNING checkup_id""",
        (title, age_min, age_max, required_gender),
    )
    checkup_id = cur.fetchone()["checkup_id"]
    db_conn.commit()
    return checkup_id


def test_completed_checkup_is_not_shown_again(client, db_conn, seed_user, seed_doctor, seed_checkup):
    # seed_checkup matches the seeded user (18-99, Any) and is due at first.
    resp = client.get(f"/users/{seed_user}/due-checkups")
    assert seed_checkup in [row["checkup_id"] for row in resp.json()]

    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO completed_checkup (user_id, doctor_id, checkup_id, completed_date)
           VALUES (%s, %s, %s, current_date)""",
        (seed_user, seed_doctor, seed_checkup),
    )
    db_conn.commit()

    resp = client.get(f"/users/{seed_user}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert seed_checkup not in ids


def test_checkup_outside_age_range_is_not_shown(client, db_conn, seed_insurance):
    # 30-year-old user, checkup only for ages 0-10.
    user_id = _make_user(db_conn, seed_insurance, date.today().year - 30, "Male")
    checkup_id = _make_checkup(db_conn, "Kinder-Checkup", 0, 10, "Any")

    resp = client.get(f"/users/{user_id}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert checkup_id not in ids


def test_checkup_outside_gender_range_is_not_shown(client, db_conn, seed_insurance):
    user_id = _make_user(db_conn, seed_insurance, date.today().year - 30, "Male")
    checkup_id = _make_checkup(db_conn, "Vorsorge Frauen", 18, 99, "Female")

    resp = client.get(f"/users/{user_id}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert checkup_id not in ids


def test_checkup_with_required_gender_any_is_shown_for_every_gender(client, db_conn, seed_insurance):
    user_id = _make_user(db_conn, seed_insurance, date.today().year - 30, "Female")
    checkup_id = _make_checkup(db_conn, "Allgemein-Checkup", 18, 99, "Any")

    resp = client.get(f"/users/{user_id}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert checkup_id in ids


def test_checkup_matching_age_and_gender_is_due(client, db_conn, seed_insurance):
    user_id = _make_user(db_conn, seed_insurance, date.today().year - 40, "Male")
    checkup_id = _make_checkup(db_conn, "Herz-Check", 35, 45, "Male")

    resp = client.get(f"/users/{user_id}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert checkup_id in ids
