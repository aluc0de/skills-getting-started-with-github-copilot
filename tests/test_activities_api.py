import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["alex@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 3,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_names = {"Chess Club", "Art Club"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert set(response.json()) == expected_names
    assert response.json()["Chess Club"]["participants"] == ["alex@example.com"]


def test_signup_adds_participant(client):
    # Arrange
    email = "sam@example.com"

    # Act
    response = client.post("/activities/Art Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "alex@example.com"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert client.get("/activities").json()["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "sam@example.com"

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant(client):
    # Arrange
    email = "alex@example.com"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_remove_rejects_unregistered_participant(client):
    # Arrange
    email = "sam@example.com"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "alex@example.com"
    ]


def test_remove_rejects_unknown_activity(client):
    # Arrange
    email = "sam@example.com"

    # Act
    response = client.delete("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
