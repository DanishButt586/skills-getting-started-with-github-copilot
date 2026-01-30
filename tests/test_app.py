"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert len(data["Chess Club"]["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Fake Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_registration(client):
    """Test that a student cannot register twice for the same activity"""
    email = "michael@mergington.edu"
    response = client.post(
        f"/activities/Chess Club/signup?email={email}"
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_unregister_from_activity_success(client):
    """Test successfully unregistering from an activity"""
    email = "michael@mergington.edu"
    
    # Verify student is initially registered
    assert email in activities["Chess Club"]["participants"]
    
    # Unregister
    response = client.delete(
        f"/activities/Chess Club/unregister?email={email}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_from_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/Fake Club/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered_student(client):
    """Test unregistering a student who is not registered"""
    email = "notregistered@mergington.edu"
    response = client.delete(
        f"/activities/Chess Club/unregister?email={email}"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_signup_and_unregister_flow(client):
    """Test the complete flow of signing up and then unregistering"""
    email = "testflow@mergington.edu"
    activity = "Programming Class"
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_activity_capacity_tracking(client):
    """Test that participant count updates correctly"""
    activity = "Chess Club"
    initial_count = len(activities[activity]["participants"])
    
    # Add a participant
    client.post(f"/activities/{activity}/signup?email=new@mergington.edu")
    assert len(activities[activity]["participants"]) == initial_count + 1
    
    # Remove a participant
    client.delete(f"/activities/{activity}/unregister?email=new@mergington.edu")
    assert len(activities[activity]["participants"]) == initial_count
