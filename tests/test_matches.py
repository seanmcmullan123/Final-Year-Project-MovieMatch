import pytest
from bson import ObjectId
from unittest.mock import patch, MagicMock
from flask import session

# 1. Page Loads
@patch("app.mongo")
def test_matches_page_loads(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    mock_mongo.db.matches.find.return_value = []
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert response.status_code == 200

# 2. Displays All Matches
@patch("app.mongo")
def test_display_matches(mock_mongo, client):
    user_id = str(ObjectId())
    other_user_id = ObjectId()
    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id)},
        {"_id": other_user_id, "username": "testuser", "profile_pic_url": "pic.jpg"}
    ]
    mock_mongo.db.matches.find.return_value = [
        {"user_1": ObjectId(user_id), "user_2": other_user_id}
    ]
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert b"testuser" in response.data

# 3. Each Match Shows Info
@patch("app.mongo")
def test_each_match_displays_info(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = ObjectId()
    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id)},
        {"_id": matched_user_id, "username": "coolperson", "bio": "hi", "profile_pic_url": "pic.jpg"}
    ]
    mock_mongo.db.matches.find.return_value = [
        {"user_1": ObjectId(user_id), "user_2": matched_user_id}
    ]
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert b"coolperson" in response.data
    assert b"pic.jpg" in response.data

# 4. Match Removal Works
@patch("app.mongo")
def test_match_removal(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())
    # Mock user session and user lookup
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    # Simulate match deletion response
    mock_delete_result = MagicMock()
    mock_delete_result.deleted_count = 1
    mock_mongo.db.matches.delete_one.return_value = mock_delete_result
    # Make the JSON POST request to /remove_match
    response = client.post(
        "/remove_match",
        json={"matched_user_id": matched_user_id},
        content_type="application/json"
    )
    assert response.status_code == 200
    assert response.json["success"] is True
    mock_mongo.db.matches.delete_one.assert_called_once_with({
        "$or": [
            {"user_1": ObjectId(user_id), "user_2": ObjectId(matched_user_id)},
            {"user_1": ObjectId(matched_user_id), "user_2": ObjectId(user_id)}
        ]
    })

# 5. Match Removal Updates Counter (assumes counter on page)
@patch("app.mongo")
def test_match_counter_after_removal(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    mock_mongo.db.matches.find.return_value = []
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert b"match" in response.data.lower() and b"0" in response.data

# 6. Match With Deleted User
@patch("app.mongo")
def test_deleted_user_match_cleanup(mock_mongo, client):
    user_id = str(ObjectId())
    ghost_user_id = ObjectId()
    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id)},
        None  # matched user no longer exists
    ]
    mock_mongo.db.matches.find.return_value = [
        {"_id": ObjectId(), "user_1": ObjectId(user_id), "user_2": ghost_user_id}
    ]
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert b"no matches yet" in response.data.lower()

# 7. Message Button Works
@patch("app.mongo")
def test_message_button_link(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = ObjectId()
    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id)},
        {"_id": matched_user_id, "username": "chatuser", "profile_pic_url": "pic.jpg"}
    ]
    mock_mongo.db.matches.find.return_value = [
        {"user_1": ObjectId(user_id), "user_2": matched_user_id}
    ]
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert bytes(f"/chat/{matched_user_id}", "utf-8") in response.data

# 8. Movie Swipes Button
@patch("app.mongo")
def test_movie_swipes_button_redirect(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {"_id": ObjectId(user_id)}
    mock_mongo.db.matches.find.return_value = []
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/matches")
    assert b"/swipe_movies" in response.data



#    PYTHONPATH=. pytest tests/test_matches.py


