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


def test_protocols_management_and_client_configs(client):
    admin_token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. List protocols
    proto_res = client.get("/api/v1/admin/protocols", headers=headers)
    assert proto_res.status_code == 200
    protocols = proto_res.json()
    assert len(protocols) >= 2
    proto_names = [p["protocol_name"] for p in protocols]
    assert "openvpn_tcp" in proto_names
    assert "wireguard" in proto_names

    # 2. Update OpenVPN port
    update_res = client.put("/api/v1/admin/protocols/openvpn_tcp", headers=headers, json={
        "listen_port": 8443,
        "is_enabled": True
    })
    assert update_res.status_code == 200
    assert update_res.json()["listen_port"] == 8443

    # 3. Create a test client user
    client.post("/api/v1/admin/users", headers=headers, json={
        "username": "charlie",
        "password": "CharliePassword123!",
        "allowed_protocols": "openvpn_tcp,wireguard"
    })

    # Client Login
    login_res = client.post("/api/v1/client/login", json={
        "username": "charlie",
        "password": "CharliePassword123!"
    })
    client_token = login_res.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # 4. Fetch OpenVPN client profile (.ovpn)
    ovpn_res = client.get("/api/v1/client/config/openvpn?proto=tcp", headers=client_headers)
    assert ovpn_res.status_code == 200
    ovpn_content = ovpn_res.text
    assert "client" in ovpn_content
    assert "proto tcp" in ovpn_content
    assert "<ca>" in ovpn_content
    assert "</ca>" in ovpn_content
    assert "BEGIN CERTIFICATE" in ovpn_content

    # 5. Fetch WireGuard client profile (.conf)
    wg_res = client.get("/api/v1/client/config/wireguard", headers=client_headers)
    assert wg_res.status_code == 200
    wg_content = wg_res.text
    assert "[Interface]" in wg_content
    assert "PrivateKey = " in wg_content
    assert "[Peer]" in wg_content
    assert "PublicKey = " in wg_content
    assert "AllowedIPs = 0.0.0.0/0, ::/0" in wg_content

    # 6. Protocol restart action
    action_res = client.post("/api/v1/admin/protocols/openvpn_tcp/action", headers=headers, json={"action": "restart"})
    assert action_res.status_code == 200
    assert action_res.json()["success"] is True

    # 7. Protocol logs API
    logs_res = client.get("/api/v1/admin/protocols/openvpn_tcp/logs", headers=headers)
    assert logs_res.status_code == 200
    assert len(logs_res.json()["lines"]) > 0

