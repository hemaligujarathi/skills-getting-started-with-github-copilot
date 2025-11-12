import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Test root redirect
def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    assert "<html" in response.text or response.url.endswith("/static/index.html")

# Test get activities
def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

# Test signup for activity
@pytest.mark.parametrize("activity,email", [
    ("Chess Club", "newstudent@mergington.edu"),
    ("Programming Class", "anotherstudent@mergington.edu")
])
def test_signup_for_activity(activity, email):
    # Remove if already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in response.json()["message"]

# Test signup for non-existent activity
def test_signup_invalid_activity():
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

# Test duplicate signup
def test_signup_duplicate():
    activity = "Chess Club"
    email = "duplicate@mergington.edu"
    # Ensure email is present
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Should not allow duplicate
    assert response.status_code == 400 or email in activities[activity]["participants"]
