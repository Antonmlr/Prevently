import requests
from datetime import date

BASE_URL = "http://localhost:8000"
HEADERS = {}


# --- read endpoints (no key required) ---

def get_due_checkups(user_id: int):
    r = requests.get(f"{BASE_URL}/users/{user_id}/due-checkups", timeout=5)
    r.raise_for_status()
    return r.json()

def get_completed_checkups(user_id: int):
    r = requests.get(f"{BASE_URL}/users/{user_id}/completed-checkups", timeout=5)
    r.raise_for_status()
    return r.json()

def get_insurance_checkups(insurance_id: int):
    r = requests.get(f"{BASE_URL}/insurance-providers/{insurance_id}/checkups", timeout=5)
    r.raise_for_status()
    return r.json()

def get_doctors_for_checkup(checkup_id: int, location: str = None):
    params = {"location": location} if location else None
    r = requests.get(f"{BASE_URL}/checkups/{checkup_id}/doctors", params=params, timeout=5)
    r.raise_for_status()
    return r.json()

def get_insurance_providers():
    r = requests.get(f"{BASE_URL}/insurance-providers", timeout=5)
    r.raise_for_status()
    return r.json()

def get_users():
    r = requests.get(f"{BASE_URL}/all-users", timeout=5)
    r.raise_for_status()
    return r.json()

def get_checkups():
    r = requests.get(f"{BASE_URL}/checkups", timeout=5)
    r.raise_for_status()
    return r.json()

# --- write endpoints (API key required) ---

def post_user(first_name: str, last_name: str, date_of_birth: date, gender: str, insurance_id: int):
    payload = { "first_name": first_name, "last_name": last_name, "date_of_birth": date_of_birth.isoformat(), "gender": gender, "insurance_id": insurance_id }
    r = requests.post(f"{BASE_URL}/users", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()

def post_completed_checkup(user_id: int, doctor_id: int, checkup_id: int, completed_date: date):
    payload = { "user_id": user_id, "doctor_id": doctor_id, "checkup_id": checkup_id, "completed_date": completed_date.isoformat() }
    r = requests.post(f"{BASE_URL}/completed-checkups", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()

def post_appointment(user_id: int, doctor_id: int, checkup_id: int, checkup_date: date, duration: int):
    payload = { "user_id": user_id, "doctor_id": doctor_id, "checkup_id": checkup_id, "checkup_date": checkup_date.isoformat(), "duration": duration }
    r = requests.post(f"{BASE_URL}/appointments", json=payload, headers=HEADERS, timeout=5)
    r.raise_for_status()
    return r.json()