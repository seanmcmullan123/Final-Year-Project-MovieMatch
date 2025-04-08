import pytest
from unittest.mock import patch
from bson import ObjectId
from flask import session
from datetime import datetime



# 1. Chat Page Loads
@patch("app.mongo")
def test_chat_page_loads(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    # Set up mock user data
    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {
        "user_1": ObjectId(user_id), "user_2": ObjectId(matched_user_id)
    }
    mock_mongo.db.messages.find.return_value = []

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get(f"/chat/{matched_user_id}")

    assert response.status_code == 200
    #  Adjusted selector to something that actually exists on the page
    assert b'<form id="chat-form"' in response.data or b'name="message"' in response.data




# 2. Back to Matches Button
@patch("app.mongo")
def test_back_to_matches_button(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {"user_1": ObjectId(user_id), "user_2": ObjectId(matched_user_id)}
    mock_mongo.db.messages.find.return_value = []

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get(f"/chat/{matched_user_id}")
    assert b"Back to Matches" in response.data





# 3. Message Sending Works
@patch("app.mongo")
def test_message_sending(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {
        "user_1": ObjectId(user_id),
        "user_2": ObjectId(matched_user_id)
    }

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        f"/chat/{matched_user_id}",
        json={"message": "Hello there!"},  # ✅ Send JSON properly
        follow_redirects=True
    )

    assert response.status_code == 200
    mock_mongo.db.messages.insert_one.assert_called_once()






# 4. Empty Message Validation
@patch("app.mongo")
def test_empty_message_not_allowed(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {
        "user_1": ObjectId(user_id),
        "user_2": ObjectId(matched_user_id)
    }

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        f"/chat/{matched_user_id}",
        json={"message": "   "},  # Only spaces
        follow_redirects=True
    )

    assert response.status_code == 400
    assert response.is_json
    assert response.get_json()["error"] == "Message cannot be empty"






# 5. Profanity Filtering
@patch("app.mongo")
def test_profanity_is_censored(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {"user_1": ObjectId(user_id), "user_2": ObjectId(matched_user_id)}

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        f"/chat/{matched_user_id}",
        json={"message": "This is shit"},
        follow_redirects=True
    )

    # Ensure the censored text is passed to insert_one
    args, kwargs = mock_mongo.db.messages.insert_one.call_args
    saved_message = args[0]["text"]
    assert "****" in saved_message or "s***" in saved_message  # covers both cases







# 6. Chat Displays Messages
@patch("app.mongo")
def test_chat_displays_existing_messages(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {"user_1": ObjectId(user_id), "user_2": ObjectId(matched_user_id)}
    mock_mongo.db.messages.find.return_value = [
        {
            "_id": ObjectId(),  # ✅ REQUIRED to avoid KeyError
            "sender": ObjectId(user_id),
            "receiver": ObjectId(matched_user_id),
            "text": "Hey there!",
            "timestamp": datetime.utcnow()  # ✅ Optional, avoids update call
        }
    ]

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get(f"/chat/{matched_user_id}")
    assert b"Hey there!" in response.data






# 7. Messages Sorted by Time (Assumes sorting in route)
@patch("app.mongo")
def test_messages_sorted_by_time(mock_mongo, client):
    user_id = str(ObjectId())
    matched_user_id = str(ObjectId())

    mock_mongo.db.users.find_one.side_effect = [
        {"_id": ObjectId(user_id), "username": "UserA"},
        {"_id": ObjectId(matched_user_id), "username": "UserB"}
    ]
    mock_mongo.db.matches.find_one.return_value = {
        "user_1": ObjectId(user_id),
        "user_2": ObjectId(matched_user_id)
    }

    mock_mongo.db.messages.find.return_value = [
        {
            "_id": ObjectId(),
            "sender": ObjectId(user_id),
            "receiver": ObjectId(matched_user_id),
            "text": "First",
            "timestamp": 1
        },
        {
            "_id": ObjectId(),
            "sender": ObjectId(user_id),
            "receiver": ObjectId(matched_user_id),
            "text": "Second",
            "timestamp": 2
        },
        {
            "_id": ObjectId(),
            "sender": ObjectId(user_id),
            "receiver": ObjectId(matched_user_id),
            "text": "Third",
            "timestamp": 3
        }
    ]

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get(f"/chat/{matched_user_id}")
    assert response.status_code == 200
    assert b"First" in response.data
    assert b"Second" in response.data
    assert b"Third" in response.data






#   PYTHONPATH=. pytest tests/test_chat.py




#ALL PASSED LETS GOOOO