import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_status_200():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant():
    email = "test@student.com"
    activity_name = quote("Chess Club", safe="")

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    email = "duplicate@student.com"
    activity_name = quote("Chess Club", safe="")

    first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert first_response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant():
    email = "john@mergington.edu"
    activity_name = quote("Gym Class", safe="")

    response = client.delete(f"/activities/{activity_name}/participants?email={quote(email, safe='')}" )
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from Gym Class"

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Gym Class"]["participants"]


def test_remove_missing_participant_returns_404():
    email = "missing@student.com"
    activity_name = quote("Gym Class", safe="")

    response = client.delete(f"/activities/{activity_name}/participants?email={quote(email, safe='')}" )
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
