from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, model_validator

class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=3, max_length=255)
    role: str = "employee"
    department: str = "Operations"

class EmployeeOut(EmployeeCreate):
    id: int
    active: int
    model_config = ConfigDict(from_attributes=True)

class ShiftCreate(BaseModel):
    employee_id: int
    shift_date: date
    start_time: time
    end_time: time
    role_label: str = "Shift"
    notes: str | None = None
    @model_validator(mode="after")
    def valid_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self

class ShiftOut(ShiftCreate):
    id: int
    employee_name: str | None = None
    model_config = ConfigDict(from_attributes=True)

class LeaveCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: str = ""
    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

class LeaveOut(LeaveCreate):
    id: int
    status: str
    created_at: datetime
    employee_name: str | None = None
    model_config = ConfigDict(from_attributes=True)

class AttendanceCreate(BaseModel):
    employee_id: int
    work_date: date
    clock_in: datetime | None = None
    clock_out: datetime | None = None
    status: str = "present"
