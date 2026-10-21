def test_attendance_rejects_clock_out_before_clock_in(client):
    employee = client.post("/api/employees", json={
        "name": "Clock Worker", "email": "clock@example.com",
    }).json()
    response = client.post("/api/attendance", json={
        "employee_id": employee["id"], "work_date": "2026-10-21",
        "clock_in": "2026-10-21T17:00:00", "clock_out": "2026-10-21T09:00:00",
    })
    assert response.status_code == 422


def test_attendance_csv_export(client):
    employee = client.post("/api/employees", json={
        "name": "CSV Worker", "email": "csv@example.com",
    }).json()
    created = client.post("/api/attendance", json={
        "employee_id": employee["id"], "work_date": "2026-10-21", "status": "present",
    })
    assert created.status_code == 201
    response = client.get("/api/attendance/export.csv")
    assert response.status_code == 200
    assert "CSV Worker" in response.text
    assert response.headers["content-type"].startswith("text/csv")
