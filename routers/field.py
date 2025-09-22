from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from database import get_connection

router = APIRouter()

# --------------------
# Pydantic models
# --------------------
class FieldCreate(BaseModel):
    farmer_id: int
    size_acres: float
    crop_id: int
    last_planted: Optional[date] = None

class FieldUpdate(BaseModel):
    size_acres: Optional[float] = None
    crop_id: Optional[int] = None
    last_planted: Optional[date] = None

# --------------------
# CRUD Endpoints
# --------------------

@router.post("/", summary="Create a new field")
def create_field(payload: FieldCreate):
    conn = get_connection()
    cur = conn.cursor()

    # validate farmer exists
    cur.execute("SELECT farmer_id FROM Farmer WHERE farmer_id = %s", (payload.farmer_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Farmer not found")

    # validate crop exists
    cur.execute("SELECT crop_id FROM Crop WHERE crop_id = %s", (payload.crop_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Crop not found")

    cur.execute("""
        INSERT INTO Field (farmer_id, size_acres, crop_id, last_planted)
        VALUES (%s, %s, %s, %s)
    """, (payload.farmer_id, payload.size_acres, payload.crop_id, payload.last_planted))
    conn.commit()
    last_id = cur.lastrowid

    cur.close()
    conn.close()
    return {"message": "Field created", "field_id": last_id}


@router.get("/", summary="Get all fields")
def get_fields():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Field")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@router.get("/{field_id}", summary="Get one field by ID")
def get_field(field_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM Field WHERE field_id = %s", (field_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Field not found")
    return row


@router.put("/{field_id}", summary="Update a field")
def update_field(field_id: int, payload: FieldUpdate):
    conn = get_connection()
    cur = conn.cursor()

    # make sure field exists
    cur.execute("SELECT field_id FROM Field WHERE field_id = %s", (field_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Field not found")

    # build dynamic update
    updates = []
    params = []
    if payload.size_acres is not None:
        updates.append("size_acres = %s")
        params.append(payload.size_acres)
    if payload.crop_id is not None:
        # validate crop exists
        cur.execute("SELECT crop_id FROM Crop WHERE crop_id = %s", (payload.crop_id,))
        if cur.fetchone() is None:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Crop not found")
        updates.append("crop_id = %s")
        params.append(payload.crop_id)
    if payload.last_planted is not None:
        updates.append("last_planted = %s")
        params.append(payload.last_planted)

    if not updates:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    sql = f"UPDATE Field SET {', '.join(updates)} WHERE field_id = %s"
    params.append(field_id)
    cur.execute(sql, tuple(params))
    conn.commit()

    cur.close()
    conn.close()
    return {"message": "Field updated successfully"}


@router.delete("/{field_id}", summary="Delete a field")
def delete_field(field_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Field WHERE field_id = %s", (field_id,))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"message": "Field deleted successfully"}
