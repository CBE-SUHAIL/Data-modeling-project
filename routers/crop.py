from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection

router = APIRouter()

# Pydantic model matching your tables
class Crop(BaseModel):
    crop_name: str
    season: str
    soil_suitability: str
    recommended_fertilizer: str
    growth_period_days: int

# CREATE
@router.post("/")
def create_crop(crop: Crop):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Crop (crop_name, season, soil_suitability, recommended_fertilizer, growth_period_days)
        VALUES (%s, %s, %s, %s, %s)
    """, (crop.crop_name, crop.season, crop.soil_suitability, crop.recommended_fertilizer, crop.growth_period_days))
    conn.commit()
    last_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"message": "Crop added successfully", "crop_id": last_id}

# READ all
@router.get("/")
def get_crops():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Crop")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# READ single by crop_id
@router.get("/{crop_id}")
def get_crop(crop_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Crop WHERE crop_id = %s", (crop_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Crop not found")
    return row

# UPDATE by crop_id
@router.put("/{crop_id}")
def update_crop(crop_id: int, crop: Crop):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Crop
        SET crop_name=%s, season=%s, soil_suitability=%s, recommended_fertilizer=%s, growth_period_days=%s
        WHERE crop_id=%s
    """, (crop.crop_name, crop.season, crop.soil_suitability, crop.recommended_fertilizer, crop.growth_period_days, crop_id))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Crop not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Crop updated successfully"}

# DELETE by crop_id
@router.delete("/{crop_id}")
def delete_crop(crop_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Crop WHERE crop_id=%s", (crop_id,))
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Crop not found")
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Crop deleted successfully"}
