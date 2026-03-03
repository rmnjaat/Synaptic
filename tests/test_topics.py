"""Integration tests for the Topics router."""
import pytest


def test_create_topic(client, seed_user):
    resp = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": "Binary Trees",
        "description": "Tree data structure",
        "category": "dsa",
        "is_public": True,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Binary Trees"
    assert body["data"]["status"] == "to-learn"
    assert body["data"]["progress_percentage"] == 0.0


def test_create_duplicate_topic_returns_409(client, seed_user):
    payload = {
        "user_id": seed_user.id,
        "name": "Duplicate Topic",
        "category": "backend",
    }
    client.post("/api/topics/create", json=payload)
    resp = client.post("/api/topics/create", json=payload)
    assert resp.status_code == 409


def test_get_topic(client, seed_user):
    create = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": "FastAPI Basics",
        "category": "backend",
    })
    topic_id = create.json()["data"]["id"]
    resp = client.get(f"/api/topics/{topic_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == topic_id


def test_mark_topic_completed(client, seed_user):
    create = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": "GraphQL",
        "category": "backend",
    })
    topic_id = create.json()["data"]["id"]
    resp = client.post(f"/api/topics/{topic_id}/mark-completed")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "completed"
    assert resp.json()["data"]["completed_at"] is not None


def test_mark_topic_in_progress(client, seed_user):
    create = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": "REST APIs",
        "category": "backend",
    })
    topic_id = create.json()["data"]["id"]
    resp = client.post(f"/api/topics/{topic_id}/mark-in-progress")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "in-progress"


def test_mark_topic_to_learn(client, seed_user):
    create = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": "Kafka",
        "category": "backend",
    })
    topic_id = create.json()["data"]["id"]
    # first complete it
    client.post(f"/api/topics/{topic_id}/mark-completed")
    resp = client.post(f"/api/topics/{topic_id}/mark-to-learn")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "to-learn"
    assert resp.json()["data"]["completed_at"] is None


def test_get_topic_not_found(client):
    resp = client.get("/api/topics/9999")
    assert resp.status_code == 404
