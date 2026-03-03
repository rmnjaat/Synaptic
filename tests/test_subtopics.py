"""Integration tests for SubTopics router and progress cascading."""
import pytest


def _create_topic(client, seed_user, name="Sorting Algorithms", category="dsa"):
    resp = client.post("/api/topics/create", json={
        "user_id": seed_user.id,
        "name": name,
        "category": category,
    })
    return resp.json()["data"]["id"]


def test_create_subtopic(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    resp = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Bubble Sort"})
    assert resp.status_code == 201
    assert resp.json()["data"]["name"] == "Bubble Sort"
    assert resp.json()["data"]["status"] == "to-learn"


def test_duplicate_subtopic_returns_409(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Quick Sort"})
    resp = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Quick Sort"})
    assert resp.status_code == 409


def test_get_subtopics(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Merge Sort"})
    resp = client.get(f"/api/topics/{topic_id}/subtopics")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


def test_progress_updates_on_subtopic_completion(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    s1 = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Step 1"}).json()["data"]["id"]
    s2 = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Step 2"}).json()["data"]["id"]

    # Initially 0% progress
    topic = client.get(f"/api/topics/{topic_id}").json()["data"]
    assert topic["progress_percentage"] == 0.0

    # Complete 1 of 2 → 50%
    client.post(f"/api/subtopics/{s1}/mark-completed")
    topic = client.get(f"/api/topics/{topic_id}").json()["data"]
    assert topic["progress_percentage"] == 50.0

    # Complete 2 of 2 → 100%
    client.post(f"/api/subtopics/{s2}/mark-completed")
    topic = client.get(f"/api/topics/{topic_id}").json()["data"]
    assert topic["progress_percentage"] == 100.0


def test_mark_subtopic_in_progress(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    st_id = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Heap Sort"}).json()["data"]["id"]
    resp = client.post(f"/api/subtopics/{st_id}/mark-in-progress")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "in-progress"


def test_delete_subtopic_updates_progress(client, seed_user):
    topic_id = _create_topic(client, seed_user)
    s_id = client.post(f"/api/topics/{topic_id}/subtopics/create", json={"name": "Shell Sort"}).json()["data"]["id"]
    client.post(f"/api/subtopics/{s_id}/mark-completed")
    client.delete(f"/api/subtopics/{s_id}")
    # After deletion no subtopics → progress = 0
    topic = client.get(f"/api/topics/{topic_id}").json()["data"]
    assert topic["progress_percentage"] == 0.0
