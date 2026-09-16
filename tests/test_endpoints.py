# ============================================================
#  test_endpoints.py -- "API" part of the test plan.
#
#  One test per endpoint (all 11 routes in api/main.py), the
#  requirements "Write endpoints (POST) without a valid
#  X-API-Key are refused", and the acceptance criterion "a record
#  that violates a constraint is rejected by the API (4xx)" for
#  every POST route.
# ============================================================


# ---- GET endpoints ---------------------------------------------

def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "API läuft"}


def test_due_checkups_returns_matching_checkup(client, seed_user, seed_checkup):
    resp = client.get(f"/users/{seed_user}/due-checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert seed_checkup in ids


def test_completed_checkups_returns_seeded_entry(client, db_conn, seed_user, seed_doctor, seed_checkup):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO completed_checkup (user_id, doctor_id, checkup_id, completed_date)
           VALUES (%s, %s, %s, current_date)""",
        (seed_user, seed_doctor, seed_checkup),
    )
    db_conn.commit()

    resp = client.get(f"/users/{seed_user}/completed-checkups")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["checkup_id"] == seed_checkup
    assert body[0]["doctor_name"] == "Dr. Test"


def test_insurance_provider_checkups(client, db_conn, seed_insurance, seed_checkup):
    cur = db_conn.cursor()
    cur.execute(
        """INSERT INTO included_checkup (insurance_id, checkup_id, coverage_amount)
           VALUES (%s, %s, 50)""",
        (seed_insurance, seed_checkup),
    )
    db_conn.commit()

    resp = client.get(f"/insurance-providers/{seed_insurance}/checkups")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["coverage_amount"] == 50


def test_doctors_for_checkup(client, seed_medical_checkup):
    doctor_id, checkup_id = seed_medical_checkup
    resp = client.get(f"/checkups/{checkup_id}/doctors")
    assert resp.status_code == 200
    ids = [row["doctor_id"] for row in resp.json()]
    assert doctor_id in ids


def test_doctors_for_checkup_filters_by_location(client, seed_medical_checkup):
    _doctor_id, checkup_id = seed_medical_checkup
    resp = client.get(f"/checkups/{checkup_id}/doctors", params={"location": "Nirgendwo"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_all_insurance_providers(client, seed_insurance):
    resp = client.get("/insurance-providers")
    assert resp.status_code == 200
    ids = [row["insurance_id"] for row in resp.json()]
    assert seed_insurance in ids


def test_all_users(client, seed_user):
    resp = client.get("/all-users")
    assert resp.status_code == 200
    ids = [row["user_id"] for row in resp.json()]
    assert seed_user in ids


def test_all_checkups(client, seed_checkup):
    resp = client.get("/checkups")
    assert resp.status_code == 200
    ids = [row["checkup_id"] for row in resp.json()]
    assert seed_checkup in ids


# ---- POST endpoints ---------------------------------------------

def test_create_user(client, api_key_header, seed_insurance):
    resp = client.post(
        "/users",
        headers=api_key_header,
        json={
            "first_name": "Neu",
            "last_name": "User",
            "date_of_birth": "1995-05-05",
            "gender": "Female",
            "insurance_id": seed_insurance,
        },
    )
    assert resp.status_code == 201
    assert "user_id" in resp.json()


def test_create_completed_checkup(client, api_key_header, seed_user, seed_doctor, seed_checkup):
    resp = client.post(
        "/completed-checkups",
        headers=api_key_header,
        json={
            "user_id": seed_user,
            "doctor_id": seed_doctor,
            "checkup_id": seed_checkup,
            "completed_date": "2026-01-01",
        },
    )
    assert resp.status_code == 201
    assert "completed_id" in resp.json()


def test_create_completed_checkup_rejects_unknown_ids(client, api_key_header, seed_user):
    resp = client.post(
        "/completed-checkups",
        headers=api_key_header,
        json={
            "user_id": seed_user,
            "doctor_id": 999999,
            "checkup_id": 999999,
            "completed_date": "2026-01-01",
        },
    )
    assert resp.status_code == 404


def test_create_user_rejects_unknown_insurance_id(client, api_key_header):
    """Acceptance criterion: a record that violates a constraint (here: an
    insurance_id that doesn't exist) is rejected by the API with a 4xx,
    not a 500."""
    resp = client.post(
        "/users",
        headers=api_key_header,
        json={
            "first_name": "Neu",
            "last_name": "User",
            "date_of_birth": "1995-05-05",
            "gender": "Female",
            "insurance_id": 999999,
        },
    )
    assert resp.status_code == 404


def test_create_appointment(client, api_key_header, seed_user, seed_doctor, seed_checkup):
    resp = client.post(
        "/appointments",
        headers=api_key_header,
        json={
            "user_id": seed_user,
            "doctor_id": seed_doctor,
            "checkup_id": seed_checkup,
            "checkup_date": "2026-02-01",
            "duration": 30,
        },
    )
    assert resp.status_code == 201
    assert "appointment_id" in resp.json()


def test_create_appointment_rejects_unknown_ids(client, api_key_header, seed_user, seed_checkup):
    resp = client.post(
        "/appointments",
        headers=api_key_header,
        json={
            "user_id": seed_user,
            "doctor_id": 999999,
            "checkup_id": seed_checkup,
            "checkup_date": "2026-02-01",
            "duration": 30,
        },
    )
    assert resp.status_code == 404


def test_create_appointment_rejects_non_positive_duration(client, api_key_header, seed_user, seed_doctor, seed_checkup):
    resp = client.post(
        "/appointments",
        headers=api_key_header,
        json={
            "user_id": seed_user,
            "doctor_id": seed_doctor,
            "checkup_id": seed_checkup,
            "checkup_date": "2026-02-01",
            "duration": 0,
        },
    )
    assert resp.status_code == 400


# ---- Acceptance criterion: X-API-Key is enforced -----------------

def test_create_user_without_api_key_is_refused(client, seed_insurance):
    resp = client.post(
        "/users",
        json={
            "first_name": "Neu",
            "last_name": "User",
            "date_of_birth": "1995-05-05",
            "gender": "Female",
            "insurance_id": seed_insurance,
        },
    )
    assert resp.status_code in (401, 422)


def test_create_user_with_wrong_api_key_is_refused(client, seed_insurance):
    resp = client.post(
        "/users",
        headers={"X-API-Key": "wrong-key"},
        json={
            "first_name": "Neu",
            "last_name": "User",
            "date_of_birth": "1995-05-05",
            "gender": "Female",
            "insurance_id": seed_insurance,
        },
    )
    assert resp.status_code == 401


def test_create_completed_checkup_without_api_key_is_refused(client, seed_user, seed_doctor, seed_checkup):
    resp = client.post(
        "/completed-checkups",
        json={
            "user_id": seed_user,
            "doctor_id": seed_doctor,
            "checkup_id": seed_checkup,
            "completed_date": "2026-01-01",
        },
    )
    assert resp.status_code in (401, 422)


def test_create_appointment_without_api_key_is_refused(client, seed_user, seed_doctor, seed_checkup):
    resp = client.post(
        "/appointments",
        json={
            "user_id": seed_user,
            "doctor_id": seed_doctor,
            "checkup_id": seed_checkup,
            "checkup_date": "2026-02-01",
            "duration": 30,
        },
    )
    assert resp.status_code in (401, 422)
