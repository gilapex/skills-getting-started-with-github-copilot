"""Tests for the activities API endpoints"""

def test_root_redirect(client):
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client, reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert len(data) == 9


def test_get_activities_structure(client, reset_activities):
    """Test that activity data has correct structure"""
    response = client.get("/activities")
    activities = response.json()
    
    activity = activities["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity_success(client, reset_activities):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Basketball Team/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    assert "Basketball Team" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "test@mergington.edu" in activities["Basketball Team"]["participants"]


def test_signup_activity_not_found(client, reset_activities):
    """Test signup for non-existent activity"""
    response = client.post(
        "/activities/Non-Existent Activity/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_registered(client, reset_activities):
    """Test signup when already registered"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_unregister_success(client, reset_activities):
    """Test successful unregister from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "michael@mergington.edu" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister from non-existent activity"""
    response = client.delete(
        "/activities/Non-Existent Activity/unregister",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_registered(client, reset_activities):
    """Test unregister when not registered"""
    response = client.delete(
        "/activities/Basketball Team/unregister",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_signup_then_unregister_flow(client, reset_activities):
    """Test complete flow of signup and unregister"""
    email = "flow@mergington.edu"
    activity = "Soccer Club"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify signed up
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregistered
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]
