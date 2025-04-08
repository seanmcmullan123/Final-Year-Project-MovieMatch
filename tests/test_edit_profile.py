import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from flask import session
from app import app
from io import BytesIO



@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# 1. Page loads
@patch("app.mongo")
def test_edit_profile_page_loads(mock_mongo, client):
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(), "username": "user", "fav_movies": [], "fav_actors": [], "fav_genres": []
    }
    with client.session_transaction() as sess:
        sess["user_id"] = str(ObjectId())
    response = client.get("/edit_profile")
    assert response.status_code == 200
    assert b"<title>Edit Profile</title>" in response.data  # ✅ updated assertion


# 2. Cancel button works
@patch("app.mongo")
def test_cancel_button_present(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "fav_movies": [],
        "fav_actors": [],
        "fav_genres": [],
        "gender_preference": "Both"
    }

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/edit_profile")
    assert response.status_code == 200
    assert b"Cancel" in response.data  # or check for href or button label


# 3. Save profile successfully
@patch("app.mongo")
def test_successful_profile_update(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/edit_profile", data={
        "username": "validuser",
        "bio": "This is my bio",
        "fun_fact": "Fun fact here",
        "gender_preference": "Both",
        "fav_movies": '["Inception"]',
        "fav_actors": '["Leonardo DiCaprio"]',
        "fav_genres": '["Action"]'
    }, follow_redirects=True)
    assert b"Profile updated successfully!" in response.data


# 4. Validation - fields can't be blank
@patch("app.mongo")
def test_blank_fields_rejected(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/edit_profile", data={
        "username": "",
        "bio": "",
        "fun_fact": "",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Username must be at least 6 characters long." in response.data


# 5. Validation - profanity check
@patch("app.mongo")
@patch("app.profanity.contains_profanity")
def test_profanity_fields(mock_profanity, mock_mongo, client):
    user_id = str(ObjectId())

    # Setup mocks
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    mock_profanity.side_effect = lambda x: x == "shituser"

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post("/edit_profile", data={
        "username": "shituser",
        "bio": "clean",
        "fun_fact": "clean",
        "gender_preference": "Both"
    }, follow_redirects=True)

    assert b"Username contains inappropriate language." in response.data


# 6. Duplicate username
@patch("app.mongo")
def test_duplicate_username(mock_mongo, client):
    user_id = str(ObjectId())

    # First call to find_one returns current user (editing their own profile)
    # Second call simulates another user already using that username
    def side_effect_find_one(query):
        if query == {"_id": ObjectId(user_id)}:
            return {"_id": ObjectId(user_id), "username": "currentuser"}
        elif query == {"username": "existinguser"}:
            return {"_id": ObjectId(), "username": "existinguser"}
        return None

    mock_mongo.db.users.find_one.side_effect = side_effect_find_one

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post("/edit_profile", data={
        "username": "existinguser",
        "bio": "Valid bio here",
        "fun_fact": "Interesting fact",
        "gender_preference": "Both"
    }, follow_redirects=True)

    assert b"Username already taken" in response.data


# 7. Profile picture update (mocking Azure upload)
@patch("app.mongo")
@patch("app.container_client")
def test_profile_pic_update(mock_blob, mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    data = {
        "username": "validuser",
        "bio": "Updated bio",
        "fun_fact": "Updated fact",
        "gender_preference": "Both",
        "profile_pic": (BytesIO(b"fake image"), "profile.jpg")
    }
    response = client.post("/edit_profile", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Profile updated successfully!" in response.data


# 8. Update all valid fields
@patch("app.mongo")
def test_update_all_valid_fields(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/edit_profile", data={
        "username": "fullupdate",
        "bio": "Long enough bio",
        "fun_fact": "Fun enough fact",
        "gender_preference": "Both",
        "fav_movies": '["Movie 1", "Movie 2"]',
        "fav_actors": '["Actor 1"]',
        "fav_genres": '["Drama", "Thriller"]'
    }, follow_redirects=True)
    assert b"Profile updated successfully!" in response.data


# 9. Changing genres updates movieswipe (Mock - you'll need genre logic in swipe route)
@patch("app.mongo")
def test_genres_affect_movieswipe(mock_mongo, client):
    user_id = str(ObjectId())

    def find_one_side_effect(query):
        if query == {"_id": ObjectId(user_id)}:
            # This is called multiple times, return user each time
            return {
                "_id": ObjectId(user_id),
                "username": "user",
                "bio": "Some bio",
                "fun_fact": "Some fun",
                "profile_pic_url": "https://fake.url/pic.jpg",
                "fav_movies": [],
                "fav_actors": [],
                "fav_genres": [],
                "gender_preference": "Both"
            }
        elif query == {"username": "newuser"}:
            # No conflict with this username
            return None
        return None

    mock_mongo.db.users.find_one.side_effect = find_one_side_effect

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post("/edit_profile", data={
        "username": "newuser",
        "bio": "Some bio",
        "fun_fact": "Some fun",
        "gender_preference": "Both",
        "fav_genres": '["Horror"]',
        "fav_movies": "[]",
        "fav_actors": "[]"
    }, follow_redirects=True)

    assert b"Profile updated successfully!" in response.data



# 10. Username must meet length
@patch("app.mongo")
def test_short_username_rejected(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/edit_profile", data={
        "username": "yo",
        "bio": "Valid bio",
        "fun_fact": "Valid fact",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Username must be at least 6 characters" in response.data


# 11. Bio + Fun fact length
@patch("app.mongo")
def test_short_bio_or_fun_fact(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.post("/edit_profile", data={
        "username": "validuser",
        "bio": "bio",
        "fun_fact": "fact",
        "gender_preference": "Both"
    }, follow_redirects=True)
    assert b"Bio must be at least 6 characters long" in response.data








 
#    PYTHONPATH=. pytest tests/test_edit_profile.py





