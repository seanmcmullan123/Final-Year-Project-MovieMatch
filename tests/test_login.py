from unittest.mock import patch
from bson import ObjectId
from werkzeug.security import generate_password_hash
import pytest



# 1. Login page loads
@patch("app.mongo")
def test_login_page_loads(mock_mongo, client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login to MovieMatch" in response.data


# 2. Link to register page
@patch("app.mongo")
def test_register_link_works(mock_mongo, client):
    response = client.get("/login")
    assert b"Register here" in response.data


# 3. Successful login with valid user
@patch("app.mongo")
def test_login_success(mock_mongo, client):
    fake_user_id = str(ObjectId())
    hashed_password = generate_password_hash("Valid1234")
    mock_user = {"_id": ObjectId(fake_user_id), "username": "validuser", "password": hashed_password}
    mock_mongo.db.users.find_one.return_value = mock_user

    with client.session_transaction() as sess:
        sess["user_id"] = fake_user_id

    response = client.post("/login", data={
        "username": "validuser",
        "password": "Valid1234"
    }, follow_redirects=True)

    #  Instead of looking for flash message, look for something on the profile page
    assert b"Your MovieMatch Profile" in response.data  # Or change to a unique heading in profile.html


#4 . Login fails if username is wrong
@patch("app.mongo")
def test_login_wrong_username(mock_mongo, client):
    # Simulate that no user is found with the given username
    mock_mongo.db.users.find_one.return_value = None

    response = client.post("/login", data={
        "username": "wronguser",
        "password": "AnyPass123"
    }, follow_redirects=True)

    assert b"Invalid username or password" in response.data
    assert b"Please register if you haven&#39;t." in response.data  # HTML-escaped apostrophe


#5 . Login fails if password is wrong
@patch("app.mongo")
def test_login_wrong_password(mock_mongo, client):
    hashed_password = generate_password_hash("Correct123")
    mock_user = {"_id": ObjectId(), "username": "testuser", "password": hashed_password}
    mock_mongo.db.users.find_one.return_value = mock_user

    response = client.post("/login", data={
        "username": "testuser",
        "password": "WrongPass"
    }, follow_redirects=True)

    assert b"Invalid username or password" in response.data
    assert b"Please register if you haven&#39;t." in response.data  # HTML escaped version


# 6. Login fails if username is blank
@patch("app.mongo")
def test_login_blank_username(mock_mongo, client):
    response = client.post("/login", data={
        "username": "",
        "password": "Valid123"
    }, follow_redirects=True)
    assert b"Please fill in both fields" in response.data


# 7. Login fails if password is blank
@patch("app.mongo")
def test_login_blank_password(mock_mongo, client):
    response = client.post("/login", data={
        "username": "normaluser",
        "password": ""
    }, follow_redirects=True)
    assert b"Please fill in both fields" in response.data




    #   PYTHONPATH=. pytest tests/test_login.py
