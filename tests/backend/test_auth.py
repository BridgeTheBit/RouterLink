def test_setup_flow_and_login(client):
    # 1. Setup status initially requires setup
    res = client.get("/api/v1/auth/setup/status")
    assert res.status_code == 200
    assert res.json()["is_setup_required"] is True

    # 2. Setup superadmin
    res = client.post("/api/v1/auth/setup", json={
        "username": "admin",
        "password": "SuperSecurePassword123!",
        "confirm_password": "SuperSecurePassword123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "superadmin"

    # 3. Setup status now False
    res = client.get("/api/v1/auth/setup/status")
    assert res.json()["is_setup_required"] is False

    # 4. Reject duplicate setup
    res = client.post("/api/v1/auth/setup", json={
        "username": "admin2",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    assert res.status_code == 400

    # 5. Admin login with correct password
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "SuperSecurePassword123!"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

    # 6. Admin login with wrong password
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

