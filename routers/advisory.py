from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from datetime import date

router = APIRouter()

# Pydantic model for advisory (optional, for GET/POST if needed)
class Advisory(BaseModel):
    farmer_id: int
    message: str
    date: date

# GET all advisories
@router.get("/")
def get_advisories():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Advisory ORDER BY date DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Function to generate advisories automatically
def generate_advisories():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch all fields with crop and farmer info
    cur.execute("""
        SELECT f.field_id, f.farmer_id, f.last_planted, c.crop_name, c.growth_period_days, c.recommended_fertilizer
        FROM Field f
        JOIN Crop c ON f.crop_id = c.crop_id
    """)
    fields = cur.fetchall()

    today = date.today()

    for field in fields:
        days_since_planting = (today - field['last_planted']).days

        # Rule 1: weekly check
        if days_since_planting % 7 == 0:
            message = f"Check {field['crop_name']} in Field {field['field_id']} – weekly maintenance required"
            cur.execute("""
                INSERT INTO Advisory (farmer_id, message, date)
                VALUES (%s, %s, %s)
            """, (field['farmer_id'], message, today))

        # Rule 2: fertilizer reminder every 14 days
        if days_since_planting % 14 == 0:
            message = f"Apply {field['recommended_fertilizer']} to {field['crop_name']} in Field {field['field_id']}"
            cur.execute("""
                INSERT INTO Advisory (farmer_id, message, date)
                VALUES (%s, %s, %s)
            """, (field['farmer_id'], message, today))

    conn.commit()
    cur.close()
    conn.close()

# POST endpoint to manually trigger advisory generation
@router.post("/generate")
def create_advisories():
    generate_advisories()
    return {"message": "Advisories generated successfully"}
