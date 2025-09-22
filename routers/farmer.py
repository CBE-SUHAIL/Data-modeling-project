from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection

router = APIRouter()

# Pydantic model for validation
class Farmer(BaseModel):
    name: str
    phone_number: str
    soil_type: str
    latitude: float
    longitude: float

# CREATE
@router.post("/")
def create_farmer(farmer: Farmer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Farmer (name, phone_number, soil_type, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s)
    """, (farmer.name, farmer.phone_number, farmer.soil_type, farmer.latitude, farmer.longitude))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Farmer added successfully"}

# READ all
@router.get("/")
def get_farmers():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Farmer")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# READ one
@router.get("/{farmer_id}")
def get_farmer(farmer_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Farmer WHERE farmer_id = %s", (farmer_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return row

# UPDATE
@router.put("/{farmer_id}")
def update_farmer(farmer_id: int, farmer: Farmer):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Farmer SET name=%s, phone_number=%s, soil_type=%s, latitude=%s, longitude=%s
        WHERE farmer_id=%s
    """, (farmer.name, farmer.phone_number, farmer.soil_type, farmer.latitude, farmer.longitude, farmer_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Farmer updated successfully"}

# DELETE
@router.delete("/{farmer_id}")
def delete_farmer(farmer_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Farmer WHERE farmer_id=%s", (farmer_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Farmer deleted successfully"}
