from __future__ import annotations


def test_user_device_session_message_memory_and_audit_flow(client, admin_headers):
    user = client.post(
        "/admin/users",
        headers=admin_headers,
        json={"username": "ronny", "display_name": "Ronny", "role": "owner"},
    )
    assert user.status_code == 201, user.text
    user_id = user.json()["id"]

    device = client.post(
        "/admin/devices",
        headers=admin_headers,
        json={"name": "phone", "owner_user_id": user_id, "device_type": "mobile"},
    )
    assert device.status_code == 201, device.text
    device_id = device.json()["id"]

    session = client.post(
        "/sessions",
        headers=admin_headers,
        json={"user_id": user_id, "device_id": device_id, "title": "Planning"},
    )
    assert session.status_code == 201, session.text
    session_id = session.json()["id"]

    message = client.post(
        f"/sessions/{session_id}/messages",
        headers=admin_headers,
        json={"role": "user", "content": "Remember PiGenus is continuity."},
    )
    assert message.status_code == 201, message.text

    detail = client.get(f"/sessions/{session_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["messages"][0]["content"] == "Remember PiGenus is continuity."

    updated = client.patch(
        f"/sessions/{session_id}",
        headers=admin_headers,
        json={"summary": "PiGenus continuity note captured."},
    )
    assert updated.status_code == 200
    assert updated.json()["summary"] == "PiGenus continuity note captured."

    memory = client.post(
        "/memory",
        headers=admin_headers,
        json={
            "namespace": "charter",
            "key": "identity",
            "value": "Reliable private orchestration node",
            "importance": 100,
        },
    )
    assert memory.status_code == 201, memory.text

    found = client.get("/memory?query=orchestration", headers=admin_headers)
    assert found.status_code == 200
    assert found.json()[0]["key"] == "identity"

    audit = client.get("/admin/audit", headers=admin_headers)
    assert audit.status_code == 200
    actions = {event["action"] for event in audit.json()}
    assert "user.created" in actions
    assert "memory.created" in actions


def test_manual_maintenance_creates_jobs(client, admin_headers):
    result = client.post("/admin/maintenance/run", headers=admin_headers)
    assert result.status_code == 200, result.text
    assert result.json()["maintenance_jobs_created"] >= 1

    status = client.get("/admin/status", headers=admin_headers)
    assert status.status_code == 200
    assert status.json()["jobs_queued"] >= 1
