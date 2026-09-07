import psycopg2
import psycopg2.extras
import psycopg2.errors
import os
from fastapi import FastAPI, HTTPException, Header, Depends
from typing import Optional
from datetime import date
from pydantic import BaseModel

app = FastAPI(title="Prevently-API")

DATABASE_URL = os.environ["DATABASE_URL"]

def get_connection():
    return psycopg2.connect(DATABASE_URL)

EXPECTED_TOKEN = os.environ["API_KEY"]

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/")
def root():
    return {"status": "API läuft"}

# Get Api Endpoints

@app.get("/users/{user_id}/due-checkups")
def due_checkups(user_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.checkup_id, c.title, c.age_min, c.age_max, c.required_gender
        FROM checkup c
        JOIN prevently_user u ON u.user_id = %s
        WHERE EXTRACT(YEAR FROM age(current_date, u.date_of_birth)) BETWEEN c.age_min AND c.age_max
          AND (c.required_gender = u.gender OR c.required_gender = 'Any')
          AND NOT EXISTS (
              SELECT 1 FROM completed_checkup cc
              WHERE cc.checkup_id = c.checkup_id AND cc.user_id = u.user_id
          )
        ORDER BY c.title
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/users/{user_id}/completed-checkups")
def completed_checkups(user_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.checkup_id, c.title, c.age_min, c.age_max, c.required_gender
        FROM completed_checkup cc
        JOIN checkup c ON c.checkup_id = cc.checkup_id
        WHERE cc.user_id = %s
        ORDER BY c.title
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/insurance-providers/{id}/checkups")
def insurance_provider_checkups(id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT c.checkup_id, c.title, ic.coverage_amount
        FROM checkup c
        JOIN included_checkup ic ON ic.checkup_id = c.checkup_id
        WHERE ic.insurance_id = %s
        ORDER BY c.title
    """, (id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/checkups/{checkup_id}/doctors")
def doctors_for_checkup(checkup_id: int, location: Optional[str] = None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    query = """
        SELECT d.doctor_id, d.d_name, d.location
        FROM doctor d
        JOIN medical_checkup mc ON mc.doctor_id = d.doctor_id
        WHERE mc.checkup_id = %s
    """
    params = [checkup_id]

    if location:
        query += " AND d.location = %s"
        params.append(location)

    query += " ORDER BY d.d_name"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/insurance-providers")
def all_insurance_providers():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT insurance_id, i_name FROM insurance_provider ORDER BY i_name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/users")
def all_users():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT user_id, first_name, last_name
        FROM prevently_user
        ORDER BY last_name, first_name
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/checkups")
def all_checkups():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT checkup_id, title, age_min, age_max, required_gender
        FROM checkup
        ORDER BY title
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# POST Api Endpoints

# Classes for the API endpoints
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str

class CompletedCheckupCreate(BaseModel):
    user_id: int
    doctor_id: int
    checkup_id: int
    completed_date: date

class AppointmentCreate(BaseModel):
    user_id: int
    doctor_id: int
    checkup_id: int
    checkup_date: date
    duration: int

@app.post("/users", status_code=201, dependencies=[Depends(verify_api_key)])
def create_user(user: UserCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO prevently_user (first_name, last_name, date_of_birth, gender)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
            """,
            (user.first_name, user.last_name, user.date_of_birth, user.gender),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return {"user_id": new_id}


@app.post("/completed-checkups", status_code=201, dependencies=[Depends(verify_api_key)])
def create_completed_checkup(entry: CompletedCheckupCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO completed_checkup (user_id, doctor_id, checkup_id, completed_date)
            VALUES (%s, %s, %s, %s)
            RETURNING completed_id
            """,
            (entry.user_id, entry.doctor_id, entry.checkup_id, entry.completed_date),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(status_code=404, detail="user_id, doctor_id oder checkup_id existiert nicht.")
    finally:
        cursor.close()
        conn.close()
    return {"completed_id": new_id}


@app.post("/appointments", status_code=201, dependencies=[Depends(verify_api_key)])
def create_appointment(appointment: AppointmentCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO appointment (user_id, doctor_id, checkup_id, checkup_date, duration)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING appointment_id
            """,
            (appointment.user_id, appointment.doctor_id, appointment.checkup_id,
             appointment.checkup_date, appointment.duration),
        )
        new_id = cursor.fetchone()[0]
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(status_code=404, detail="user_id, doctor_id oder checkup_id existiert nicht.")
    except psycopg2.errors.CheckViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="duration muss größer als 0 sein.")
    finally:
        cursor.close()
        conn.close()
    return {"appointment_id": new_id}
