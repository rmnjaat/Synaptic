"""Integration tests for the Global Search endpoint."""


def _seed(client, seed_user):
    user_id = seed_user.id
    client.post("/api/topics/create", json={"user_id": user_id, "name": "Algorithm Basics", "category": "dsa"})
    client.post("/api/topics/create", json={"user_id": user_id, "name": "Flask REST APIs", "category": "backend"})
    return user_id


def test_search_finds_topic_by_name(client, seed_user):
    user_id = _seed(client, seed_user)
    resp = client.get(f"/api/search/global?user_id={user_id}&q=algo")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["total_count"] >= 1
    assert any("Algorithm" in t["name"] for t in body["data"]["topics"])


def test_search_short_query_returns_422(client, seed_user):
    resp = client.get(f"/api/search/global?user_id={seed_user.id}&q=a")
    # FastAPI validates min_length=2 on the Query param and returns 422 Unprocessable Entity
    assert resp.status_code == 422


def test_search_no_results(client, seed_user):
    resp = client.get(f"/api/search/global?user_id={seed_user.id}&q=zzznomatches")
    assert resp.status_code == 200
    assert resp.json()["data"]["total_count"] == 0


def test_search_across_notes(client, seed_user):
    user_id = seed_user.id
    topic_resp = client.post("/api/topics/create", json={
        "user_id": user_id, "name": "System Design", "category": "system_design"
    })
    topic_id = topic_resp.json()["data"]["id"]
    client.post("/api/notes/create", json={
        "user_id": user_id, "topic_id": topic_id,
        "title": "CAP Theorem Notes", "content": "Consistency Availability Partition",
    })
    resp = client.get(f"/api/search/global?user_id={user_id}&q=CAP")
    body = resp.json()
    assert body["data"]["total_count"] >= 1
    assert any("CAP" in n["title"] for n in body["data"]["notes"])
