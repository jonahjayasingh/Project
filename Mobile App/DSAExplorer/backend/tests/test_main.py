import pytest

def test_home(client):
    print("\nRunning test: test_home")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello"}

def test_register_user(client):
    print("\nRunning test: test_register_user")
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "account has been created successfully" in response.json()["message"]

def test_register_duplicate_user(client):
    print("\nRunning test: test_register_duplicate_user")
    # First registration
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    # Duplicate registration
    response = client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with that name already exists"

def test_login_success(client):
    print("\nRunning test: test_login_success")
    # Register first
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    # Login
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["username"] == "testuser"

def test_login_invalid_credentials(client):
    print("\nRunning test: test_login_invalid_credentials")
    # Register first
    client.post(
        "/register",
        json={"username": "testuser", "password": "testpassword"}
    )
    # Login with wrong password
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"

def test_bookmark_flow(client):
    print("\nRunning test: test_bookmark_flow")
    # Register and Login
    client.post("/register", json={"username": "testuser", "password": "testpassword"})
    login_res = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add bookmark
    response = client.post(
        "/addbookmark",
        json={"algorithm_id": "binary_search"},
        headers=headers
    )
    assert response.status_code == 200
    assert "Bookmark for user" in response.json()["message"]

    # Get bookmarks
    response = client.get("/getbookmarks", headers=headers)
    assert response.status_code == 200
    bookmarks = response.json()
    assert len(bookmarks) == 1
    assert bookmarks[0]["algorithm_id"] == "binary_search"
    bookmark_id = bookmarks[0]["id"]

    # Check bookmark
    response = client.get(f"/checkbookmark/{bookmark_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_bookmarked"] is True

    # Delete bookmark
    response = client.delete(f"/deletebookmark/{bookmark_id}", headers=headers)
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    # Get bookmarks again
    response = client.get("/getbookmarks", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
