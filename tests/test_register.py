from unittest.mock import patch
from bson import ObjectId
from werkzeug.security import generate_password_hash
import pytest


@patch("app.mongo")
def test_registration_page_loads(mock_mongo, client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Your MovieMatch Account" in response.data


@patch("app.mongo")
def test_login_link_works(mock_mongo, client):
    response = client.get("/register")
    assert b"Already have an account?" in response.data
    assert b"Login here" in response.data


@patch("app.mongo")
def test_register_user_success(mock_mongo, client):
    mock_mongo.db.users.find_one.return_value = None
    response = client.post("/register", data={
        "username": "validuser",
        "email": "valid@email.com",
        "password": "Valid123",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Registration successful" in response.data


@patch("app.mongo")
def test_short_username(mock_mongo, client):
    response = client.post("/register", data={
        "username": "se",
        "email": "test@email.com",
        "password": "Valid123",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Username must be at least 6 characters" in response.data


@patch("app.mongo")
def test_short_password(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "test@email.com",
        "password": "Vi1",  # too short
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    
    assert b"Password must be at least 8 characters and contain a number." in response.data


@patch("app.mongo")
def test_password_missing_number(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "test@email.com",
        "password": "Password",  # valid length but no number
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    
    assert b"Password must be at least 8 characters and contain a number." in response.data


@patch("app.mongo")
def test_email_invalid_format(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "invalidemail",
        "password": "Valid123",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Invalid email format" in response.data


@patch("app.mongo")
def test_profanity_fields(mock_mongo, client):
    response = client.post("/register", data={
        "username": "bitch",
        "email": "bitch@email.com",
        "password": "bitch123",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"inappropriate language" in response.data


@patch("app.mongo")
def test_underage_user(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "test@email.com",
        "password": "Valid123",
        "dob": "2015-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"You must be at least 18 years old" in response.data


@patch("app.mongo")
def test_missing_required_fields(mock_mongo, client):
    response = client.post("/register", data={
        "username": "",
        "email": "",
        "password": "",
        "dob": "",
        "gender": "",
        "gender_preference": ""
    }, follow_redirects=True)

    assert b"Please fill out all fields, including gender." in response.data


@patch("app.mongo")
def test_duplicate_username(mock_mongo, client):
    mock_mongo.db.users.find_one.return_value = {"username": "existinguser"}
    response = client.post("/register", data={
        "username": "existinguser",
        "email": "unique@email.com",
        "password": "Valid123",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Username already exists" in response.data


@patch("app.mongo")
def test_duplicate_email(mock_mongo, client):
    # First call = no user by username, second call = email already exists
    mock_mongo.db.users.find_one.side_effect = [None, {"email": "test@email.com"}]
    
    response = client.post("/register", data={
        "username": "newuser",
        "email": "test@email.com",
        "password": "Valid1234",
        "dob": "2000-01-01",
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)

    assert b"Email already exists." in response.data


@patch("app.mongo")
def test_invalid_dob_format(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "valid@email.com",
        "password": "Valid1234",
        "dob": "20-04-2020",  # Wrong format
        "gender": "Male",
        "gender_preference": "Both"
    }, follow_redirects=True)

    assert b"Invalid date format." in response.data


@patch("app.mongo")
def test_gender_fields_unselected(mock_mongo, client):
    response = client.post("/register", data={
        "username": "validuser",
        "email": "valid@email.com",
        "password": "Valid1234",
        "dob": "2000-01-01",
        "gender": "",  # not selected
        "gender_preference": ""  # not selected
    }, follow_redirects=True)

    assert b"Please fill out all fields, including gender." in response.data




#    PYTHONPATH=. pytest tests/test_register.py




#ALL PASSED LETS GOOOO