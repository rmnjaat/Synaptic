"""Integration tests for Projects router."""


def test_create_project(client, seed_user):
    resp = client.post("/api/projects/create", json={
        "user_id": seed_user.id,
        "name": "Algorithm Visualizer",
        "description": "Visualize sorting algorithms",
        "tech_stack": "React, FastAPI",
        "status": "planning",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Algorithm Visualizer"
    assert body["data"]["status"] == "planning"


def test_mark_project_completed(client, seed_user):
    create = client.post("/api/projects/create", json={
        "user_id": seed_user.id,
        "name": "Chat App",
        "status": "in-progress",
    })
    project_id = create.json()["data"]["id"]
    resp = client.post(f"/api/projects/{project_id}/mark-completed")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"
    assert resp.json()["data"]["completed_at"] is not None


def test_add_topics_to_project(client, seed_user):
    user_id = seed_user.id
    t_id = client.post("/api/topics/create", json={
        "user_id": user_id, "name": "WebSockets", "category": "backend"
    }).json()["data"]["id"]
    p_id = client.post("/api/projects/create", json={
        "user_id": user_id, "name": "Real-time Dashboard", "status": "planning"
    }).json()["data"]["id"]
    resp = client.post(f"/api/projects/{p_id}/add-topics", json={"topic_ids": [t_id]})
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_get_user_projects(client, seed_user):
    user_id = seed_user.id
    client.post("/api/projects/create", json={"user_id": user_id, "name": "Project Alpha", "status": "planning"})
    client.post("/api/projects/create", json={"user_id": user_id, "name": "Project Beta", "status": "in-progress"})
    resp = client.get(f"/api/users/{user_id}/projects")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2


def test_get_project_not_found(client):
    resp = client.get("/api/projects/9999")
    assert resp.status_code == 404
