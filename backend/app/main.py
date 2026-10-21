import csv
import io
import os
import time as time_module
from datetime import date, time
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, SessionLocal
from . import models, schemas

app = FastAPI(title="ShiftPilot API", version="0.1.0", description="Employee scheduling and attendance MVP")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    for attempt in range(20):
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                if not db.scalar(select(models.Employee.id).limit(1)):
                    employees = [
                        models.Employee(name="Alex Morgan", email="alex@example.com", role="manager", department="Operations"),
                        models.Employee(name="Jamie Lee", email="jamie@example.com", role="employee", department="Support"),
                        models.Employee(name="Sam Rivera", email="sam@example.com", role="employee", department="Support"),
                    ]
                    db.add_all(employees); db.commit(); db.refresh(employees[0]); db.refresh(employees[1]); db.refresh(employees[2])
                    db.add_all([
                        models.Shift(employee_id=employees[0].id, shift_date=date.today(), start_time=time(9), end_time=time(17), role_label="Team lead"),
                        models.Shift(employee_id=employees[1].id, shift_date=date.today(), start_time=time(10), end_time=time(18), role_label="Support"),
                    ])
                    db.commit()
            return
        except OperationalError:
            if attempt == 19: raise
            time_module.sleep(2)

@app.get("/health")
def health(): return {"status": "ok", "service": "shiftpilot-api"}

@app.get("/api/employees", response_model=list[schemas.EmployeeOut])
def list_employees(active_only: bool = True, db: Session = Depends(get_db)):
    stmt = select(models.Employee).order_by(models.Employee.name)
    if active_only: stmt = stmt.where(models.Employee.active == 1)
    return db.scalars(stmt).all()

@app.post("/api/employees", response_model=schemas.EmployeeOut, status_code=201)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    item = models.Employee(**payload.model_dump())
    db.add(item)
    try: db.commit(); db.refresh(item)
    except IntegrityError: db.rollback(); raise HTTPException(409, "An employee with this email already exists")
    return item

@app.get("/api/shifts")
def list_shifts(start: date | None = None, end: date | None = None, db: Session = Depends(get_db)):
    stmt = select(models.Shift, models.Employee.name).join(models.Employee, models.Employee.id == models.Shift.employee_id).order_by(models.Shift.shift_date, models.Shift.start_time)
    if start: stmt = stmt.where(models.Shift.shift_date >= start)
    if end: stmt = stmt.where(models.Shift.shift_date <= end)
    return [{"id": s.id, "employee_id": s.employee_id, "employee_name": name, "shift_date": s.shift_date.isoformat(), "start_time": s.start_time.strftime("%H:%M"), "end_time": s.end_time.strftime("%H:%M"), "role_label": s.role_label, "notes": s.notes} for s, name in db.execute(stmt).all()]

@app.post("/api/shifts", status_code=201)
def create_shift(payload: schemas.ShiftCreate, db: Session = Depends(get_db)):
    if not db.get(models.Employee, payload.employee_id): raise HTTPException(404, "Employee not found")
    item = models.Shift(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, **payload.model_dump(mode="json"), "employee_name": item.employee.name}

@app.delete("/api/shifts/{shift_id}", status_code=204)
def delete_shift(shift_id: int, db: Session = Depends(get_db)):
    item = db.get(models.Shift, shift_id)
    if not item: raise HTTPException(404, "Shift not found")
    db.delete(item); db.commit(); return Response(status_code=204)

@app.get("/api/leaves")
def list_leaves(db: Session = Depends(get_db)):
    stmt = select(models.LeaveRequest, models.Employee.name).join(models.Employee).order_by(models.LeaveRequest.created_at.desc())
    return [{"id": x.id, "employee_id": x.employee_id, "employee_name": name, "start_date": x.start_date.isoformat(), "end_date": x.end_date.isoformat(), "reason": x.reason, "status": x.status, "created_at": x.created_at.isoformat()} for x, name in db.execute(stmt).all()]

@app.post("/api/leaves", status_code=201)
def create_leave(payload: schemas.LeaveCreate, db: Session = Depends(get_db)):
    if not db.get(models.Employee, payload.employee_id): raise HTTPException(404, "Employee not found")
    item = models.LeaveRequest(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, **payload.model_dump(mode="json"), "status": item.status, "created_at": item.created_at.isoformat()}

@app.patch("/api/leaves/{leave_id}/status")
def update_leave_status(leave_id: int, status: str = Query(..., pattern="^(approved|rejected|pending)$"), db: Session = Depends(get_db)):
    item = db.get(models.LeaveRequest, leave_id)
    if not item: raise HTTPException(404, "Leave request not found")
    item.status = status; db.commit(); db.refresh(item)
    return {"id": item.id, "status": item.status}

@app.get("/api/attendance")
def list_attendance(db: Session = Depends(get_db)):
    stmt = select(models.Attendance, models.Employee.name).join(models.Employee).order_by(models.Attendance.work_date.desc())
    return [{"id": a.id, "employee_id": a.employee_id, "employee_name": name, "work_date": a.work_date.isoformat(), "clock_in": a.clock_in.isoformat() if a.clock_in else None, "clock_out": a.clock_out.isoformat() if a.clock_out else None, "status": a.status} for a, name in db.execute(stmt).all()]

@app.post("/api/attendance", status_code=201)
def create_attendance(payload: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    if not db.get(models.Employee, payload.employee_id): raise HTTPException(404, "Employee not found")
    if payload.clock_in and payload.clock_out and payload.clock_out < payload.clock_in: raise HTTPException(422, "clock_out must not be before clock_in")
    item = models.Attendance(**payload.model_dump()); db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, **payload.model_dump(mode="json")}

@app.get("/api/attendance/export.csv")
def export_attendance(db: Session = Depends(get_db)):
    stmt = select(models.Attendance, models.Employee.name).join(models.Employee).order_by(models.Attendance.work_date.desc())
    buffer = io.StringIO(); writer = csv.writer(buffer)
    writer.writerow(["id", "employee", "date", "clock_in", "clock_out", "status"])
    for a, name in db.execute(stmt).all(): writer.writerow([a.id, name, a.work_date.isoformat(), a.clock_in.isoformat() if a.clock_in else "", a.clock_out.isoformat() if a.clock_out else "", a.status])
    return Response(content=buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=shiftpilot-attendance.csv"})
