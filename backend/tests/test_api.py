def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "shiftpilot-api"}


def test_invalid_shift_time_rejected(client):
    response = client.post("/api/shifts", json={
        "employee_id": 1,
        "shift_date": "2026-10-21",
        "start_time": "18:00:00",
        "end_time": "09:00:00",
        "role_label": "Test",
    })
    assert response.status_code == 422
