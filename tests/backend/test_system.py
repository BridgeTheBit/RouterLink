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


def test_system_stats_and_backups(client):
    admin_token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. System stats
    stats_res = client.get("/api/v1/admin/system/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "cpu_percent" in stats
    assert "ram_used_mb" in stats
    assert "total_users" in stats

    # 2. Create backup
    backup_res = client.post("/api/v1/admin/system/backups", headers=headers)
    assert backup_res.status_code == 200
    assert "filename" in backup_res.json()

    # 3. List backups
    list_res = client.get("/api/v1/admin/system/backups", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

