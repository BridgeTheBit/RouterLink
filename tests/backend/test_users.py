def get_admin_token(client):
    client.post("/api/v1/auth/setup", json={
        "username": "admin",
        "password": "SuperAdminPass123!",
        "confirm_password": "SuperAdminPass123!"
    })
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "SuperAdminPass123!"
    })
    return res.json()["access_token"]


def test_user_lifecycle_and_quota(client):
    token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a user with 5GB quota (5 * 1024 * 1024 * 1024)
    five_gb = 5 * 1024 * 1024 * 1024
    create_res = client.post("/api/v1/admin/users", headers=headers, json={
        "username": "alice",
        "password": "AliceSecret123!",
        "email": "alice@example.com",
        "traffic_limit_bytes": five_gb,
        "max_concurrent_connections": 2,
        "max_registered_devices": 3,
        "allowed_protocols": "openvpn_tcp,wireguard"
    })
    assert create_res.status_code == 201
    user_data = create_res.json()
    user_id = user_data["id"]
    assert user_data["username"] == "alice"
    assert user_data["traffic_limit_bytes"] == five_gb
    assert user_data["remaining_traffic_bytes"] == five_gb
    assert user_data["can_connect"] is True

    # 2. Get user list
    list_res = client.get("/api/v1/admin/users", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. Update user settings (modify allowed protocols)
    update_res = client.put(f"/api/v1/admin/users/{user_id}", headers=headers, json={
        "allowed_protocols": "wireguard"
    })
    assert update_res.status_code == 200
    assert update_res.json()["allowed_protocols"] == "wireguard"

    # 4. Add quota
    extra_one_gb = 1 * 1024 * 1024 * 1024
    quota_res = client.post(f"/api/v1/admin/users/{user_id}/quota", headers=headers, json={
        "additional_traffic_bytes": extra_one_gb
    })
    assert quota_res.status_code == 200
    assert quota_res.json()["traffic_limit_bytes"] == five_gb + extra_one_gb

    # 5. Delete user
    del_res = client.delete(f"/api/v1/admin/users/{user_id}", headers=headers)
    assert del_res.status_code == 204

    # 6. Verify user is gone
    get_res = client.get(f"/api/v1/admin/users/{user_id}", headers=headers)
    assert get_res.status_code == 404

