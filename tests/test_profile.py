import pytest
from unittest.mock import patch
from bson import ObjectId



# 1. Loads profile page
@patch("app.mongo")
def test_profile_page_loads(mock_mongo, client):
    mock_user = {
        "_id": ObjectId(),
        "username": "testuser",
        "bio": "Movie lover",
        "fun_fact": "I can quote every Marvel movie",
        "profile_pic": "profile.jpg"
    }
    mock_mongo.db.users.find_one.return_value = mock_user

    with client.session_transaction() as sess:
        sess["user_id"] = str(mock_user["_id"])

    response = client.get("/profile")
    assert response.status_code == 200
    assert b"testuser" in response.data or b"Your Profile" in response.data




# 2. Logout clears session and redirects
def test_logout_clears_session(client):
    with client.session_transaction() as sess:
        sess["user_id"] = "someid"

    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data or b"Register" in response.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess




# 3. Delete account removes user and clears session
@patch("app.mongo")
def test_delete_account(mock_mongo, client):
    user_id = str(ObjectId())
    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post("/delete_account", follow_redirects=True)

    # Check Mongo deletion
    mock_mongo.db.users.delete_one.assert_called_once_with({"_id": ObjectId(user_id)})

    #  Check JSON response
    assert response.is_json
    assert response.get_json() == {"success": True}

    #  Check session is cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess






# 4. Edit profile button visible / works
@patch("app.mongo")
def test_edit_profile_button(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "bio": "Something",
        "fun_fact": "Fun fact",
        "profile_pic": "img.jpg"
    }

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/profile")
    assert b"Edit Profile" in response.data




# 5. MovieSwipes button only works when profile is complete
@patch("app.mongo")
def test_movie_swipes_requires_complete_profile(mock_mongo, client):
    user_id = str(ObjectId())
    incomplete_user = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "bio": "",  # Incomplete
        "fun_fact": "Cool fact",
        "profile_pic_url": ""  # Incomplete
    }

    mock_mongo.db.users.find_one.return_value = incomplete_user

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/swipe_movies", follow_redirects=True)

    # Match the exact flash message in your route
    assert b"Complete your profile to proceed." in response.data




# 6. MovieSwipes button only works when profile is complete
@patch("app.mongo")
def test_movie_swipes_access_when_profile_complete(mock_mongo, client):
    user_id = str(ObjectId())
    complete_user = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "bio": "This is a bio.",
        "fun_fact": "Cool fact",
        "profile_pic_url": "https://example.com/image.jpg"
    }

    mock_mongo.db.users.find_one.return_value = complete_user

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/swipe_movies", follow_redirects=True)

    # The page should load successfully (status 200)
    assert response.status_code == 200

    # You can also check for some key content from your swipe page
    assert b"Swipe" in response.data or b"Movie" in response.data  # Adjust as needed




# 7. Session data correctly pulls user info
@patch("app.mongo")
def test_session_user_data_persists(mock_mongo, client):
    user_id = str(ObjectId())
    user_data = {
        "_id": ObjectId(user_id),
        "username": "testuser",
        "bio": "Movie lover",
        "fun_fact": "Fun fact",
        "profile_pic": "pic.jpg"
    }
    mock_mongo.db.users.find_one.return_value = user_data

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/profile")
    assert b"testuser" in response.data
    assert b"Movie lover" in response.data






#   PYTHONPATH=. pytest tests/test_profile.py



