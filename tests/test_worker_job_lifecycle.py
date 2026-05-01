from __future__ import annotations


def register_worker(client, admin_headers, name="thinkpad-x1", capabilities=None):
    response = client.post(
        "/workers/register",
        headers=admin_headers,
        json={"name": name, "capabilities": capabilities or ["python", "llm-api"]},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_admin_auth_required(client):
    response = client.post("/jobs", json={"job_type": "test.echo"})
    assert response.status_code == 401


def test_worker_registration_heartbeat_and_job_success(client, admin_headers):
    worker = register_worker(client, admin_headers)
    worker_headers = {"Authorization": f"Bearer {worker['token']}"}

    heartbeat = client.post(
        f"/workers/{worker['worker_id']}/heartbeat",
        headers=worker_headers,
        json={"status": "online"},
    )
    assert heartbeat.status_code == 200, heartbeat.text
    assert heartbeat.json()["status"] == "online"

    submitted = client.post(
        "/jobs",
        headers=admin_headers,
        json={
            "job_type": "memory.summarize",
            "payload": {"session_id": 1},
            "required_capabilities": ["llm-api"],
        },
    )
    assert submitted.status_code == 201, submitted.text
    job_id = submitted.json()["id"]

    lease = client.post(
        f"/jobs/lease/{worker['worker_id']}",
        headers=worker_headers,
        json={"max_jobs": 1},
    )
    assert lease.status_code == 200, lease.text
    leased_jobs = lease.json()["jobs"]
    assert len(leased_jobs) == 1
    assert leased_jobs[0]["id"] == job_id
    assert leased_jobs[0]["status"] == "leased"

    ack = client.post(
        f"/jobs/{job_id}/ack/{worker['worker_id']}",
        headers=worker_headers,
        json={"result": {"summary": "done"}},
    )
    assert ack.status_code == 200, ack.text
    assert ack.json()["status"] == "succeeded"
    assert ack.json()["result"] == {"summary": "done"}


def test_capability_filtering(client, admin_headers):
    worker = register_worker(client, admin_headers, capabilities=["python"])
    worker_headers = {"Authorization": f"Bearer {worker['token']}"}

    submitted = client.post(
        "/jobs",
        headers=admin_headers,
        json={"job_type": "gpu.render", "required_capabilities": ["gpu"]},
    )
    assert submitted.status_code == 201

    lease = client.post(
        f"/jobs/lease/{worker['worker_id']}",
        headers=worker_headers,
        json={"max_jobs": 1},
    )
    assert lease.status_code == 200
    assert lease.json()["jobs"] == []


def test_job_failure_can_requeue(client, admin_headers):
    worker = register_worker(client, admin_headers)
    worker_headers = {"Authorization": f"Bearer {worker['token']}"}

    submitted = client.post(
        "/jobs",
        headers=admin_headers,
        json={"job_type": "api.call", "required_capabilities": ["llm-api"], "max_attempts": 2},
    )
    job_id = submitted.json()["id"]

    lease = client.post(
        f"/jobs/lease/{worker['worker_id']}",
        headers=worker_headers,
        json={"max_jobs": 1},
    )
    assert lease.json()["jobs"][0]["status"] == "leased"

    failed = client.post(
        f"/jobs/{job_id}/fail/{worker['worker_id']}",
        headers=worker_headers,
        json={"error": "temporary upstream failure", "retry": True},
    )
    assert failed.status_code == 200, failed.text
    assert failed.json()["status"] == "queued"
    assert failed.json()["error"] == "temporary upstream failure"

