"""Integration tests for user progress endpoints — updated for dynamic categories."""


def test_get_user_progress_empty(client, seed_user):
    """When user has no topics, progress should return 0% overall and empty categories."""
    resp = client.get(f"/api/users/{seed_user.id}/progress")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["overall_progress"] == 0.0
    # Dynamic: no topics = no categories in response (not hardcoded 8)
    assert body["data"]["categories"] == {}


def test_get_user_progress_with_topics(client, seed_user):
    user_id = seed_user.id
    # Create 2 DSA topics and complete one
    t1 = client.post("/api/topics/create", json={"user_id": user_id, "name": "Arrays",       "category": "dsa"}).json()["data"]["id"]
    t2 = client.post("/api/topics/create", json={"user_id": user_id, "name": "Linked Lists", "category": "dsa"}).json()["data"]["id"]
    client.post(f"/api/topics/{t1}/mark-completed")

    resp = client.get(f"/api/users/{user_id}/progress")
    body = resp.json()
    assert resp.status_code == 200
    cats = body["data"]["categories"]
    # The server returns the fancy display name; find the dsa entry via category_key
    dsa_data = next((v for v in cats.values() if v.get("category_key") == "dsa"), None)
    assert dsa_data is not None, f"Expected dsa key in: {list(cats.keys())}"
    assert dsa_data["total_topics"] == 2
    assert dsa_data["completed"] == 1
    assert dsa_data["progress_percentage"] == 50.0


def test_get_category_progress(client, seed_user):
    user_id = seed_user.id
    client.post("/api/topics/create", json={"user_id": user_id, "name": "Django", "category": "backend"})
    resp = client.get(f"/api/users/{user_id}/categories/backend")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_topics"] == 1
    assert data["category"] == "backend"


def test_get_category_custom_returns_empty(client, seed_user):
    """Querying a category that has no topics returns 0 topics — not a 400."""
    resp = client.get(f"/api/users/{seed_user.id}/categories/my_custom_cat")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["total_topics"] == 0
    assert data["category"] == "my_custom_cat"


def test_get_user_topics(client, seed_user):
    user_id = seed_user.id
    client.post("/api/topics/create", json={"user_id": user_id, "name": "Docker", "category": "devops"})
    resp = client.get(f"/api/users/{user_id}/topics")
    assert resp.status_code == 200
    cats = resp.json()["data"]["topics_by_category"]
    assert len(cats["devops"]) == 1
    assert cats["devops"][0]["name"] == "Docker"


def test_create_topic_with_custom_category(client, seed_user):
    """Topics with a fully custom category string should be created and returned correctly."""
    user_id = seed_user.id
    resp = client.post("/api/topics/create", json={
        "user_id": user_id, "name": "Word2Vec", "category": "machine_learning"
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["category"] == "machine_learning"

    # Progress should now show machine_learning as its own category
    p = client.get(f"/api/users/{user_id}/progress").json()
    keys = [v.get("category_key") for v in p["data"]["categories"].values()]
    assert "machine_learning" in keys
