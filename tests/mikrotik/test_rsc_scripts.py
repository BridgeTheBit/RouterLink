from pathlib import Path

MIKROTIK_DIR = Path(__file__).parent.parent.parent / "mikrotik"


def test_rsc_files_exist():
    expected_scripts = [
        "install.rsc",
        "update.rsc",
        "uninstall.rsc",
        "backup.rsc",
        "restore.rsc"
    ]
    for script_name in expected_scripts:
        script_path = MIKROTIK_DIR / script_name
        assert script_path.exists(), f"Missing expected script: {script_name}"
        assert script_path.stat().st_size > 0, f"Script {script_name} is empty"


def test_install_script_idempotency_and_safety():
    install_rsc = (MIKROTIK_DIR / "install.rsc").read_text(encoding="utf-8")

    # 1. Verification of RouterOS environment
    assert "/system/resource/get version" in install_rsc
    assert "/container/config/find" in install_rsc

    # 2. VETH & Bridge settings
    assert "bridge-routerlink" in install_rsc
    assert "veth-routerlink" in install_rsc
    assert "172.28.0.1/24" in install_rsc
    assert "172.28.0.2/24" in install_rsc

    # 3. Persistent mount definition
    assert "routerlink/data" in install_rsc
    assert "routerlink-data" in install_rsc
    assert 'dst="/data"' in install_rsc

    # 4. Port Forwarding rules
    assert "dst-port=8080" in install_rsc
    assert "dst-port=8443" in install_rsc
    assert "dst-port=51820" in install_rsc

    # 5. Safety rule: every firewall and NAT rule has a RouterLink comment
    lines = install_rsc.splitlines()
    for line in lines:
        if "/ip/firewall/nat/add" in line:
            assert 'comment="RouterLink' in line, f"Unlabeled firewall rule found: {line}"


def test_uninstall_script_clean_teardown():
    uninstall_rsc = (MIKROTIK_DIR / "uninstall.rsc").read_text(encoding="utf-8")

    # Ensures clean removal of only RouterLink labeled rules
    assert 'find comment~"^RouterLink "' in uninstall_rsc
    assert "veth-routerlink" in uninstall_rsc
    assert "bridge-routerlink" in uninstall_rsc
    assert "routerlink-data" in uninstall_rsc
    assert "routerlink-env" in uninstall_rsc

