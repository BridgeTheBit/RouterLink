from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.session import Session as VPNSession
from app.services.session_service import SessionService
from app.workers.accounting import AccountingWorker


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


def test_concurrent_connections_and_quota_cutoff(client, db):
    admin_token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create a user with 10MB quota and max 1 concurrent connection
    ten_mb = 10 * 1024 * 1024
    create_res = client.post("/api/v1/admin/users", headers=headers, json={
        "username": "bob",
        "password": "BobPassword123!",
        "traffic_limit_bytes": ten_mb,
        "max_concurrent_connections": 1,
        "allowed_protocols": "openvpn_tcp,wireguard"
    })
    assert create_res.status_code == 201
    user_id = create_res.json()["id"]

    # 2. Client logs in via Mobile API
    login_res = client.post("/api/v1/client/login", json={
        "username": "bob",
        "password": "BobPassword123!"
    })
    assert login_res.status_code == 200
    client_token = login_res.json()["access_token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}

    # 3. Client sends 1st heartbeat -> establishes Session 1
    hb1 = client.post("/api/v1/client/heartbeat", headers=client_headers, json={
        "device_id": "phone-1",
        "protocol": "openvpn_tcp",
        "upload_delta_bytes": 1024 * 1024, # 1MB
        "download_delta_bytes": 1024 * 1024 # 1MB
    })
    assert hb1.status_code == 200
    assert hb1.json()["can_continue"] is True
    session1_token = hb1.json()["session_token"]
    assert hb1.json()["used_traffic_bytes"] == 2 * 1024 * 1024

    # 4. Attempt 2nd concurrent connection from a different device -> Rejected due to limit = 1!
    hb2 = client.post("/api/v1/client/heartbeat", headers=client_headers, json={
        "device_id": "tablet-2",
        "protocol": "openvpn_tcp",
        "upload_delta_bytes": 0,
        "download_delta_bytes": 0
    })
    assert hb2.status_code == 200
    assert hb2.json()["can_continue"] is False
    assert hb2.json()["status"] == "concurrent_limit_exceeded"

    # 5. Device 1 consumes remaining 9MB traffic (Total becomes 11MB > 10MB quota)
    hb3 = client.post("/api/v1/client/heartbeat", headers=client_headers, json={
        "session_token": session1_token,
        "device_id": "phone-1",
        "upload_delta_bytes": 4 * 1024 * 1024,
        "download_delta_bytes": 5 * 1024 * 1024
    })
    assert hb3.status_code == 200
    # Immediately cuts off because user depleted quota!
    assert hb3.json()["can_continue"] is False
    assert hb3.json()["status"] == "quota_depleted"

    # 6. Verify client profile shows depleted quota
    prof_res = client.get("/api/v1/client/profile", headers=client_headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["is_quota_depleted"] is True
    assert prof_res.json()["can_connect"] is False


def test_accounting_worker_enforcement(client, db):
    admin_token = get_admin_token(client)
    headers = {"Authorization": f"Bearer {admin_token}"}

    # 1. Create user with future expiration date
    future_date = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    client.post("/api/v1/admin/users", headers=headers, json={
        "username": "expired_user",
        "password": "Password123!",
        "expires_at": future_date,
        "traffic_limit_bytes": 0
    })

    # Start a valid active session in DB
    user = db.query(User).filter(User.username == "expired_user").first()
    session = SessionService.start_session(
        db=db,
        user_id=user.id,
        protocol="openvpn_tcp",
        device_id_str="dev-expired"
    )
    session_id = session.id

    # 2. Simulate expiration while connected
    user.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    db.commit()

    # 3. Run the accounting worker cycle directly
    worker = AccountingWorker(interval_seconds=10)
    # Patch session factory inside worker test
    from app.workers import accounting
    original_session_local = accounting.SessionLocal
    accounting.SessionLocal = lambda: db

    try:
        terminated = worker.enforce_quotas_and_expirations()
        assert terminated >= 1
        refreshed_session = db.query(VPNSession).filter(VPNSession.id == session_id).first()
        assert refreshed_session.is_active is False
        assert refreshed_session.disconnected_at is not None
    finally:
        accounting.SessionLocal = original_session_local
