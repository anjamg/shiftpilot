def test_create_shift_requires_existing_employee(client):
    response = client.post("/api/shifts", json={
        "employee_id": 999, "shift_date": "2026-10-21",
        "start_time": "09:00", "end_time": "17:00", "role_label": "Support",
    })
    assert response.status_code == 404


def test_create_and_delete_shift(client):
    employee = client.post("/api/employees", json={
        "name": "Shift Worker", "email": "shift@example.com",
    }).json()
    payload = {
        "employee_id": employee["id"], "shift_date": "2026-10-21",
        "start_time": "09:00", "end_time": "17:00", "role_label": "Support",
    }
    created = client.post("/api/shifts", json=payload)
    assert created.status_code == 201
    assert created.json()["employee_name"] == "Shift Worker"
    assert client.delete(f"/api/shifts/{created.json()['id']}").status_code == 204
