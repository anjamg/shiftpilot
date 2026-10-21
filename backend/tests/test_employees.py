def test_create_and_list_employee(client):
    created = client.post("/api/employees", json={
        "name": "Taylor Example", "email": "taylor@example.com",
        "role": "employee", "department": "Support",
    })
    assert created.status_code == 201
    assert created.json()["email"] == "taylor@example.com"
    listed = client.get("/api/employees")
    assert listed.status_code == 200
    assert any(item["email"] == "taylor@example.com" for item in listed.json())


def test_duplicate_employee_email_returns_conflict(client):
    payload = {"name": "Taylor", "email": "same@example.com"}
    assert client.post("/api/employees", json=payload).status_code == 201
    duplicate = client.post("/api/employees", json={**payload, "name": "Taylor Two"})
    assert duplicate.status_code == 409
