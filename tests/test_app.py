from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate_signup():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure email is not present initially; if it is, try to remove it first
    resp = client.get("/activities")
    participants = resp.json().get(activity, {}).get("participants", [])
    if email in participants:
        client.delete(f"/activities/{quote(activity, safe='')}/participants", params={"email": email})

    # Signup should succeed
    resp = client.post(f"/activities/{quote(activity, safe='')}/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Duplicate signup should fail with 400
    resp = client.post(f"/activities/{quote(activity, safe='')}/signup", params={"email": email})
    assert resp.status_code == 400


def test_unregister_participant():
    activity = "Chess Club"
    email = "pytest_remove@example.com"

    # Ensure the participant exists
    client.post(f"/activities/{quote(activity, safe='')}/signup", params={"email": email})

    # Now remove the participant
    resp = client.delete(f"/activities/{quote(activity, safe='')}/participants", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Confirm they're no longer in the activity
    resp = client.get("/activities")
    participants = resp.json().get(activity, {}).get("participants", [])
    assert email not in participants
