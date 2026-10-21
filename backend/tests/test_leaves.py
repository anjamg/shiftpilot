def test_leave_lifecycle(client):
    employee = client.post("/api/employees", json={
        "name": "Leave Worker", "email": "leave@example.com",
    }).json()
    created = client.post("/api/leaves", json={
        "employee_id": employee["id"], "start_date": "2026-11-01",
        "end_date": "2026-11-03", "reason": "Family",
    })
    assert created.status_code == 201
    leave_id = created.json()["id"]
    approved = client.patch(f"/api/leaves/{leave_id}/status?status=approved")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_leave_rejects_end_before_start(client):
    employee = client.post("/api/employees", json={
        "name": "Date Worker", "email": "dates@example.com",
    }).json()
    response = client.post("/api/leaves", json={
        "employee_id": employee["id"], "start_date": "2026-11-03",
        "end_date": "2026-11-01", "reason": "Invalid",
    })
    assert response.status_code == 422
