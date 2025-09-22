from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_connection

router = APIRouter()

# --------------------
# Pydantic models
# --------------------
class ActivityLogCreate(BaseModel):
    field_id: int
    activity_type: str
    activity_date: date
    notes: Optional[str] = None

class ActivityLogUpdate(BaseModel):
    activity_type: Optional[str] = None
    activity_date: Optional[date] = None
    notes: Optional[str] = None

# --------------------
# CRUD Endpoints
# --------------------

@router.post("/", summary="Create a new activity log")
def create_activity(payload: ActivityLogCreate):
    conn = get_connection()
    cur = conn.cursor()

    # validate field exists
    cur.execute("SELECT field_id FROM Field WHERE field_id = %s", (payload.field_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Field not found")

    cur.execute("""
        INSERT INTO ActivityLog (field_id, activity_type, activity_date, notes)
        VALUES (%s, %s, %s, %s)
    """, (payload.field_id, payload.activity_type, payload.activity_date, payload.notes))
    conn.commit()
    last_id = cur.lastrowid

    cur.close()
    conn.close()
    return {"message": "Activity log created", "log_id": last_id}


@router.get("/", summary="Get all activity logs")
def get_activities():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ActivityLog")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@router.get("/{log_id}", summary="Get a single activity log")
def get_activity(log_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM ActivityLog WHERE log_id = %s", (log_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return row


@router.put("/{log_id}", summary="Update an activity log")
def update_activity(log_id: int, payload: ActivityLogUpdate):
    conn = get_connection()
    cur = conn.cursor()

    # make sure log exists
    cur.execute("SELECT log_id FROM ActivityLog WHERE log_id = %s", (log_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Activity log not found")

    # build dynamic update
    updates = []
    params = []
    if payload.activity_type is not None:
        updates.append("activity_type = %s")
        params.append(payload.activity_type)
    if payload.activity_date is not None:
        updates.append("activity_date = %s")
        params.append(payload.activity_date)
    if payload.notes is not None:
        updates.append("notes = %s")
        params.append(payload.notes)

    if not updates:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    sql = f"UPDATE ActivityLog SET {', '.join(updates)} WHERE log_id = %s"
    params.append(log_id)
    cur.execute(sql, tuple(params))
    conn.commit()

    cur.close()
    conn.close()
    return {"message": "Activity log updated successfully"}


@router.delete("/{log_id}", summary="Delete an activity log")
def delete_activity(log_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ActivityLog WHERE log_id = %s", (log_id,))
    conn.commit()
    affected = cur.rowcount
    cur.close()
    conn.close()
    if affected == 0:
        raise HTTPException(status_code=404, detail="Activity log not found")
    return {"message": "Activity log deleted successfully"}
