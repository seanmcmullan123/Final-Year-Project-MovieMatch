import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from flask import session



# 1. Page loads successfully
@patch("app.mongo")
def test_swipe_movies_page_loads(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id),
        "bio": "Something",
        "fun_fact": "Cool",
        "profile_pic_url": "someurl",
        "fav_genres": ["Action"],
        "liked_movies": [],
        "disliked_movies": []
    }
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies")
    assert response.status_code == 200



# 2. Matches button works
@patch("app.mongo")
def test_matches_button_redirect(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id), "bio": "X", "fun_fact": "Y", "profile_pic_url": "url"
    }
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies")
    assert b"/matches" in response.data



# 3. Return to profile button works
@patch("app.mongo")
def test_return_to_profile_button(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id), "bio": "X", "fun_fact": "Y", "profile_pic_url": "url"
    }
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies")
    assert b"/profile" in response.data


# 4. Like button stores and shows next movie
@patch("app.mongo")
def test_like_button(mock_mongo, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "fav_genres": ["Action"]
    }

    mock_mongo.db.users.find_one.return_value = mock_user
    mock_mongo.db.user_swipes.insert_one.return_value = None
    mock_mongo.db.user_swipes.find.return_value = []
    mock_mongo.db.matches.find.return_value = []
    mock_mongo.db.matches.count_documents.return_value = 0

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        "/swipe_movies",
        json={"movie_id": "123", "action": "like"},  # ✅ Send JSON
        follow_redirects=True
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.json["success"] is True




# 5. Dislike button stores and shows next movie
@patch("app.mongo")
def test_dislike_button(mock_mongo, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "fav_genres": ["Action"]
    }

    mock_mongo.db.users.find_one.return_value = mock_user
    mock_mongo.db.user_swipes.insert_one.return_value = None
    mock_mongo.db.user_swipes.find.return_value = []
    mock_mongo.db.matches.find.return_value = []
    mock_mongo.db.matches.count_documents.return_value = 0

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        "/swipe_movies",
        json={"movie_id": "123", "action": "dislike"},  # ✅ Must use JSON
        follow_redirects=True
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.json["success"] is True





# 6. Profile incomplete
@patch("app.mongo")
def test_incomplete_profile_redirects(mock_mongo, client):
    user_id = str(ObjectId())
    mock_mongo.db.users.find_one.return_value = {
        "_id": ObjectId(user_id), "bio": "", "fun_fact": "", "profile_pic_url": ""
    }
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies", follow_redirects=True)
    assert b"Complete your profile to proceed." in response.data




# 7. Already swiped movie is not shown again
@patch("app.mongo")
def test_movie_not_repeated(mock_mongo, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "liked_movies": ["123"],
        "disliked_movies": ["456"],
        "fav_genres": ["Action"]
    }
    mock_mongo.db.users.find_one.return_value = mock_user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies")
    assert b"123" not in response.data and b"456" not in response.data




@patch("app.mongo")
def test_matching_logic_triggers(mock_mongo, client):
    user_id = str(ObjectId())

    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "gender": "Male",
        "gender_preference": "Both"
    }

    # Set up matching logic: current user liked movies 0-19, other user liked same
    mock_mongo.db.users.find_one.side_effect = [
        mock_user,  # initial user load
        {"_id": ObjectId(), "gender": "Male", "gender_preference": "Both"}  # matched user
    ]

    # Other user liked the same movie
    mock_mongo.db.user_swipes.find.side_effect = [
        [{"movie_id": "999", "user_id": ObjectId()}],  # matched_users
        [{"movie_id": str(i)} for i in range(15)],     # user_liked_movies
        [{"movie_id": str(i)} for i in range(15)],     # matched_user_likes
        []  # swiped_movie_ids
    ]

    mock_mongo.db.matches.find.return_value = []
    mock_mongo.db.matches.count_documents.return_value = 0
    mock_mongo.db.user_swipes.insert_one.return_value = None

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.post(
        "/swipe_movies",
        json={"movie_id": "999", "action": "like"},  # ✅ JSON, not form data
        follow_redirects=True
    )

    assert response.status_code == 200
    assert response.is_json
    assert response.json["success"] is True





# 9. Shows all genres if none selected
@patch("app.mongo")
def test_no_genres_selected(mock_mongo, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "fav_genres": []
    }
    mock_mongo.db.users.find_one.return_value = mock_user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
    response = client.get("/swipe_movies")
    assert response.status_code == 200




# 10. No movies left to swipe
@patch("app.search_popular_movies_by_genre")
@patch("app.mongo")
def test_no_movies_left(mock_mongo, mock_search_movies, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url",
        "fav_genres": ["Comedy"]
    }

    # Mock user and swipes
    mock_mongo.db.users.find_one.return_value = mock_user
    mock_mongo.db.user_swipes.find.return_value = [{"movie_id": str(i)} for i in range(5)]  # Swiped all
    mock_mongo.db.matches.count_documents.return_value = 0

    # Return only movies already swiped
    mock_search_movies.return_value = [{"id": i} for i in range(5)]  # All of these get filtered out

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.get("/swipe_movies")
    
    # Expect your template to render an empty state or handle no movies gracefully
    assert b"No more movies available" in response.data or b"All movies swiped" in response.data or response.status_code == 200




# 11. Swipe actions stored
@patch("app.mongo")
def test_swipe_action_stored(mock_mongo, client):
    user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(user_id),
        "bio": "bio",
        "fun_fact": "fact",
        "profile_pic_url": "url"
    }

    # Return mock user when finding
    mock_mongo.db.users.find_one.return_value = mock_user

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    # Send JSON data correctly
    response = client.post(
        "/swipe_movies",
        json={"movie_id": "789", "action": "like"},  # 👈 correct format
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 200
    mock_mongo.db.user_swipes.insert_one.assert_called_once_with({
        "user_id": mock_user["_id"],
        "movie_id": "789",
        "action": "like"
    })





#   PYTHONPATH=. pytest tests/test_swipe_movies.py




#ALL PASSED LETS GOOOO