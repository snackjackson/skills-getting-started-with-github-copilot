from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants lists so tests can modify safely
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    # restore
    for k, v in activities.items():
        v["participants"] = original[k][:]


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_prevent_duplicate():
    activity = "Chess Club"
    email = "testuser@example.com"

    # signup
    res = client.post(f"/activities/{activity}/signup?email={email}")
    assert res.status_code == 200
    assert email in activities[activity]["participants"]

    # duplicate signup should fail (400)
    res2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert res2.status_code == 400


def test_unregister_participant():
    activity = "Programming Class"
    email = "remove_me@example.com"

    # ensure participant not present then add one
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    activities[activity]["participants"].append(email)
    assert email in activities[activity]["participants"]

    # unregister
    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant_returns_404():
    activity = "Gym Class"
    email = "not_in_list@example.com"

    # ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    res = client.delete(f"/activities/{activity}/participants?email={email}")
    assert res.status_code == 404
