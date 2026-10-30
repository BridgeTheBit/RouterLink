def test_webui_static_serving(client):
    # 1. Root route serves index.html
    res = client.get("/")
    assert res.status_code == 200
    assert "RouterLink | MikroTik VPN Control Center" in res.text
    assert '<div id="app"' in res.text
    assert '<script src="/app.js"></script>' in res.text

    # 2. app.js is served
    app_res = client.get("/app.js")
    assert app_res.status_code == 200
    assert "RouterLink Web Administration Panel" in app_res.text

    # 3. SPA deep routing fallback (e.g. /dashboard or /users) serves index.html
    spa_res = client.get("/dashboard")
    assert spa_res.status_code == 200
    assert "RouterLink | MikroTik VPN Control Center" in spa_res.text

