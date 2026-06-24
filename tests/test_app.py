from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", allow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities


def test_signup_for_activity_adds_participant_and_can_cleanup():
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@example.com"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Cleanup
    cleanup_response = client.delete(signup_url, params={"email": email})
    assert cleanup_response.status_code == 200
    assert cleanup_response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_signup_for_activity_rejects_duplicate_registration():
    # Arrange
    activity_name = "Drama Club"
    email = "duplicate@example.com"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    first_response = client.post(signup_url, params={"email": email})
    second_response = client.post(signup_url, params={"email": email})

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student already signed up for this activity"

    # Cleanup
    cleanup_response = client.delete(signup_url, params={"email": email})
    assert cleanup_response.status_code == 200


def test_unregister_from_activity_removes_existing_participant():
    # Arrange
    activity_name = "Art Workshop"
    email = "removeme@example.com"
    signup_url = f"/activities/{activity_name}/signup"

    client.post(signup_url, params={"email": email})

    # Act
    response = client.delete(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_from_activity_returns_404_for_missing_participant():
    # Arrange
    activity_name = "Basketball Team"
    email = "not-registered@example.com"
    signup_url = f"/activities/{activity_name}/signup"

    # Act
    response = client.delete(signup_url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
