#I will test each route here for every single page
#python -m unittest tests/test_routes.py
#python -m unittest discover tests                  Runs all tests at once


from flask_pymongo import PyMongo
from app import app
from bson.objectid import ObjectId
import unittest
from flask import session
from unittest.mock import patch
from io import BytesIO
from datetime import datetime


class MovieMatchHomeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.ctx = app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    






    # #HOME PAGE TESTING  

    # # 1.1 Home page loads successfully
    # def test_home_page_loads(self):
    #     response = self.app.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Register', response.data)
    #     self.assertIn(b'Login', response.data)

    # # 1.2 Register button/link is on the home page and works
    # def test_register_button_redirects(self):
    #     response = self.app.get('/register')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Register', response.data)

    # # 1.3 Login button/link is on the home page and works
    # def test_login_button_redirects(self):
    #     response = self.app.get('/login')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login', response.data)










    # #REGISTER PAGE TESTING

    # def test_register_page_loads(self):
    #     response = self.app.get('/register')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Register', response.data)

    # def test_valid_registration(self):                                              ##CHANGE DATE WHEN TESTING
    #     response = self.app.post('/register', data={
    #         'username': 'testuser4410',
    #         'email': 'testuser4150@gmail.com',
    #         'password': 'Pasord41321',
    #         'dob': '2000-01-02',
    #         'gender': 'male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Registration successful', response.data)  
        

    # def test_empty_fields(self):
    #     response = self.app.post('/register', data={
    #         'username': '',
    #         'email': '',
    #         'password': '',
    #         'dob': '',
    #         'gender': ''
    #     }, follow_redirects=True)
    #     self.assertIn(b'Please fill out all fields', response.data)


    # def test_profanity_check(self):                                                 ##CHANGE DATE WHEN TESTING
    #     response = self.app.post('/register', data={
    #         'username': 'motherfucker',
    #         'email': 'cleanemail230@example.com',
    #         'password': 'Passwor3300',
    #         'dob': '2000-01-01',
    #         'gender': 'Male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Username, email, or password contains inappropriate language.', response.data)


    # def test_short_username(self):
    #     response = self.app.post('/register', data={
    #         'username': 'abc',
    #         'email': 'abc@example.com',
    #         'password': 'password123',
    #         'dob': '2000-01-01',
    #         'gender': 'Male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Username must be at least 6 characters', response.data)

    # def test_invalid_email_format(self):
    #     response = self.app.post('/register', data={
    #         'username': 'validuser',
    #         'email': 'invalidemail@',
    #         'password': 'password123',
    #         'dob': '2000-01-01',
    #         'gender': 'Male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Invalid email format', response.data)

    # def test_weak_password(self):
    #     response = self.app.post('/register', data={
    #         'username': 'validuser',
    #         'email': 'valid@example.com',
    #         'password': 'weakpass',
    #         'dob': '2000-01-01',
    #         'gender': 'Male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Password must be at least 8 characters', response.data)

    # def test_underage_user(self):
    #     response = self.app.post('/register', data={
    #         'username': 'younguser',
    #         'email': 'young@example.com',
    #         'password': 'password123',
    #         'dob': '2010-01-01',
    #         'gender': 'Male'
    #     }, follow_redirects=True)
    #     self.assertIn(b'You must be at least 18 years old', response.data)

    # def test_login_button_on_register_page(self):
    #     response = self.app.get('/register')
    #     self.assertIn(b'/login', response.data)











    # #LOGIN PAGE TESTING

    # # 3.1 Login page loads correctly
    # def test_login_page_loads(self):
    #     response = self.app.get('/login')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login', response.data)

    # # 3.2 Valid login with correct credentials
    # def test_valid_login(self):
    #     response = self.app.post('/login', data={
    #         'username': 'Steve123',  # use the correct username
    #         'password': 'Steve123'   # must match the hashed password
    #     }, follow_redirects=True)
    #     self.assertIn(b'Login successful!', response.data)

    # # 3.3 Login fails with incorrect password
    # def test_login_wrong_password(self):
    #     response = self.app.post('/login', data={
    #         'username': 'Steve123',
    #         'password': 'WrongPassword'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Invalid username or password', response.data)

    # # 3.4 Login fails with unregistered username
    # def test_login_unregistered_user(self):
    #     response = self.app.post('/login', data={
    #         'username': 'NotARealUser',
    #         'password': 'Whatever123'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Invalid username or password', response.data)

    # # 3.5 Login fails with empty fields
    # def test_login_empty_fields(self):
    #     response = self.app.post('/login', data={
    #         'username': '',
    #         'password': ''
    #     }, follow_redirects=True)
    #     # You could flash a "Please fill out all fields" message in your actual route to improve feedback.
    #     self.assertIn(b'Invalid username or password', response.data)

    # # 3.6 Profanity check on login (only works if you added this in the route)
    # def test_login_with_profanity(self):
    #     response = self.app.post('/login', data={
    #         'username': 'motherfucker',
    #         'password': 'whatever123'
    #     }, follow_redirects=True)
    #     self.assertIn(b'Invalid username or password', response.data)

    # # 3.7 Check register button/link exists on login page
    # def test_register_button_on_login_page(self):
    #     response = self.app.get('/login')
    #     self.assertIn(b'/register', response.data)













    # #PROFILE PAGE TESTING

    # def test_profile_requires_login(self):
    #     response = self.app.get('/profile', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login to MovieMatch', response.data)  # Or adjust if your login page has different heading

    # # 4.2 Profile page loads correctly when logged in
    # def test_profile_page_logged_in(self):
    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['user_id'] = '67f175795798807fa4c2c27c'  # Use a real ObjectId from your DB

    #         response = client.get('/profile')
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b'MovieMatch Profile', response.data)

    # # 4.3 Profile page shows expected user data
    # def test_profile_displays_user_data(self):
    #     with self.app as client:
    #         with client.session_transaction() as sess:
    #             sess['user_id'] = '67f175795798807fa4c2c27c'  # Same valid ObjectId

    #         response = client.get('/profile')
    #         self.assertIn(b'Username:', response.data)
    #         self.assertIn(b'Age:', response.data)
    #         self.assertIn(b'Bio:', response.data)
    #         self.assertIn(b'Fun Fact:', response.data)
    #         self.assertIn(b'Favorite Genres:', response.data)














    # # #EDIT PROFILE PAGE TESTING

    # @patch("app.mongo")
    # def test_edit_profile_page_loads(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     # Set the mocked return value for find_one
    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "This is a bio.",
    #         "fun_fact": "Something funny.",
    #         "fav_movies": ["Inception"],
    #         "fav_actors": ["DiCaprio"],
    #         "fav_genres": ["Action"],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get("/edit_profile", follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Edit Your Movie", response.data)
    #     self.assertIn(b"Match Profile", response.data)


    # @patch("app.mongo")
    # def test_short_username(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     # Mock the return from find_one
    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "Valid bio.",
    #         "fun_fact": "Valid fact.",
    #         "fav_movies": ["Inception"],
    #         "fav_actors": ["DiCaprio"],
    #         "fav_genres": ["Drama"],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     # Send POST request with short username
    #     response = self.app.post(
    #         "/edit_profile",
    #         data={
    #             "username": "abc",  # Too short
    #             "bio": "Valid bio.",
    #             "fun_fact": "Valid fact.",
    #             "gender_preference": "Both",
    #             "fav_movies": '["Inception"]',
    #             "fav_actors": '["DiCaprio"]',
    #             "fav_genres": '["Drama"]',
    #         },
    #         follow_redirects=True,
    #     )

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"at least 6 characters", response.data)




    # @patch("app.mongo")
    # def test_edit_profile_success(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "Old bio",
    #         "fun_fact": "Old fact",
    #         "fav_movies": [],
    #         "fav_actors": [],
    #         "fav_genres": [],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post("/edit_profile", data={
    #         "username": "testuser",
    #         "bio": "Loves movies!",
    #         "fun_fact": "I once met Tom Cruise!",
    #         "gender_preference": "Both",
    #         "fav_movies": '["Top Gun", "Interstellar"]',
    #         "fav_actors": '["Tom Cruise", "Matthew McConaughey"]',
    #         "fav_genres": '["Action", "Sci-Fi"]'
    #     }, follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Profile updated successfully!', response.data)




    # @patch("app.mongo")
    # def test_edit_profile_short_bio(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "Old bio",
    #         "fun_fact": "Old fact",
    #         "fav_movies": [],
    #         "fav_actors": [],
    #         "fav_genres": [],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post("/edit_profile", data={
    #         "username": "testuser",
    #         "bio": "Hi",
    #         "fun_fact": "Nice fact",
    #         "gender_preference": "Both",
    #         "fav_movies": '["Movie1"]',
    #         "fav_actors": '["Actor1"]',
    #         "fav_genres": '["Genre1"]'
    #     }, follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Bio must be at least", response.data)





    # @patch("app.mongo")
    # def test_edit_profile_profanity_in_bio(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "Old bio",
    #         "fun_fact": "Old fact",
    #         "fav_movies": [],
    #         "fav_actors": [],
    #         "fav_genres": [],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post("/edit_profile", data={
    #         "username": "testuser",
    #         "bio": "I am a bitch",
    #         "fun_fact": "Nice fact",
    #         "gender_preference": "Both",
    #         "fav_movies": '["Movie1"]',
    #         "fav_actors": '["Actor1"]',
    #         "fav_genres": '["Genre1"]'
    #     }, follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"contains inappropriate language", response.data)



    # def test_edit_profile_redirect_if_not_logged_in(self):
    #     response = self.app.get('/edit_profile', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login to MovieMatch', response.data)





    # @patch("app.mongo")
    # @patch("app.container_client")
    # def test_edit_profile_image_upload(self, mock_container_client, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     # Mock user returned from DB
    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "bio": "Existing bio",
    #         "fun_fact": "Something funny",
    #         "fav_movies": [],
    #         "fav_actors": [],
    #         "fav_genres": [],
    #         "gender_preference": "Both",
    #         "profile_pic_url": ""
    #     }

    #     # Mock the blob upload process
    #     mock_blob = mock_container_client.get_blob_client.return_value
    #     mock_blob.upload_blob.return_value = None

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     # Create a fake image file
    #     image_data = (BytesIO(b"fake image data"), "test.jpg")

    #     # Simulate POST with image
    #     response = self.app.post("/edit_profile", data={
    #         "username": "testuser",
    #         "bio": "Updated bio",
    #         "fun_fact": "Fun fact",
    #         "gender_preference": "Both",
    #         "profile_pic": image_data,
    #         "fav_movies": "[]",
    #         "fav_actors": "[]",
    #         "fav_genres": "[]"
    #     }, content_type="multipart/form-data", follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"Profile updated successfully!", response.data)

















    # #MOVIE SWIPES PAGE TESTING

    # @patch("app.mongo")
    # @patch("app.search_popular_movies_by_genre")  # You must also patch the API call
    # def test_swipe_movies_page_loads(self, mock_search_movies, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     # Mock a valid user with complete profile
    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "swipetest",
    #         "fav_genres": ["Action"],
    #         "bio": "I love movies",
    #         "fun_fact": "I met a celeb!",
    #         "profile_pic_url": "http://example.com/pic.jpg",
    #         "gender": "Male",
    #         "gender_preference": "Both"
    #     }

    #     # Mock user has swiped nothing
    #     mock_mongo.db.user_swipes.find.return_value = []

    #     # Mock movies returned from TMDB search
    #     mock_search_movies.return_value = [{
    #         "id": 123,
    #         "title": "Test Movie",
    #         "lead_actor": "Test Actor",
    #         "poster_url": "https://example.com/poster.jpg",
    #         "genre": "Action",
    #         "popularity": 100
    #     }]

    #     # Set session manually
    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get('/swipe_movies', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Test Movie', response.data)




    # @patch("app.mongo")
    # def test_swipe_movies_redirect_if_not_logged_in(self, mock_mongo):
    #     response = self.app.get('/swipe_movies', follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b'Login to MovieMatch', response.data)

    # @patch("app.mongo")
    # def test_swipe_like_post(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "swipetest",
    #         "fav_genres": ["Comedy"]
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post('/swipe_movies', data={
    #         "swipe_action": "like",
    #         "movie_id": "123abc456def789000000000"
    #     }, follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)

    # @patch("app.mongo")
    # def test_swipe_dislike_post(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "swipetest",
    #         "fav_genres": ["Comedy"]
    #     }

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post('/swipe_movies', data={
    #         "swipe_action": "dislike",
    #         "movie_id": "123abc456def789000000000"
    #     }, follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)


    # @patch("app.mongo")
    # def test_swipe_movies_resets_swipe_history_if_all_movies_swiped(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     # Setup session
    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     # Mock user with completed profile
    #     mock_mongo.db.users.find_one.return_value = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "user1",
    #         "bio": "Done",
    #         "fun_fact": "Something",
    #         "profile_pic_url": "url",
    #         "fav_genres": ["Action"],
    #         "gender": "Male",
    #         "gender_preference": "Both"
    #     }

    #     # User has swiped every movie
    #     mock_mongo.db.user_swipes.find.return_value = [{"movie_id": str(i)} for i in range(1, 1000)]

    #     # Return 0 remaining movies → triggers swipe history reset
    #     with patch("app.search_popular_movies_by_genre", return_value=[]):
    #         response = self.app.get("/swipe_movies", follow_redirects=True)

    #     self.assertEqual(response.status_code, 200)


























    # #MATCHES SWIPES PAGE TESTING
    # @patch("app.mongo")
    # def test_matches_page_loads(self, mock_mongo):
    #     fake_user_id = str(ObjectId())

    #     mock_user = {
    #         "_id": ObjectId(fake_user_id),
    #         "username": "testuser",
    #         "gender": "Male",
    #         "gender_preference": "Both"
    #     }

    #     matched_user = {
    #         "_id": ObjectId(),
    #         "username": "matchy",
    #         "gender": "Female",
    #         "profile_pic_url": "https://example.com/pic.jpg"
    #     }

    #     mock_mongo.db.users.find_one.side_effect = [mock_user, matched_user]

    #     mock_mongo.db.matches.find.return_value = [
    #         {"user_1": ObjectId(fake_user_id), "user_2": matched_user["_id"], "common_likes": 10}
    #     ]

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get("/matches")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"matchy", response.data)



    # @patch("app.mongo")
    # def test_remove_match_success(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     mock_mongo.db.matches.delete_one.return_value.deleted_count = 1

    #     response = self.app.post("/remove_match", json={
    #         "matched_user_id": matched_user_id
    #     })

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json["success"], True)



    # @patch("app.mongo")
    # def test_gender_preference_filter(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     # Mock logged in user (prefers Female only)
    #     mock_mongo.db.users.find_one.side_effect = [
    #         {
    #             "_id": ObjectId(fake_user_id),
    #             "username": "testuser",
    #             "gender": "Male",
    #             "gender_preference": "Female"
    #         },
    #         {
    #             "_id": ObjectId(matched_user_id),
    #             "username": "matchuser",
    #             "gender": "Male"  # Not Female, should be filtered out
    #         }
    #     ]

    #     mock_mongo.db.matches.find.return_value = [{
    #         "user_1": ObjectId(fake_user_id),
    #         "user_2": ObjectId(matched_user_id),
    #         "common_likes": 12
    #     }]

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get("/matches", follow_redirects=True)

    #     # Male match should be filtered out — username should not appear
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotIn(b"matchuser", response.data)





    # @patch("app.mongo")
    # def test_message_button_redirects_to_chat(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     # Mock the session user
    #     mock_mongo.db.users.find_one.side_effect = [
    #         {
    #             "_id": ObjectId(fake_user_id),
    #             "username": "testuser",
    #             "gender": "Male",
    #             "gender_preference": "Both"
    #         },
    #         {
    #             "_id": ObjectId(matched_user_id),
    #             "username": "matchuser",
    #             "gender": "Female",
    #             "profile_pic_url": "https://example.com/pic.jpg"
    #         }
    #     ]

    #     # Mock match exists
    #     mock_mongo.db.matches.find.return_value = [{
    #         "user_1": ObjectId(fake_user_id),
    #         "user_2": ObjectId(matched_user_id),
    #         "common_likes": 12
    #     }]

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get("/matches", follow_redirects=True)

    #     # Expect the match page to contain the Message button/link
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(bytes(f"/chat/{matched_user_id}", "utf-8"), response.data)


























    
    



    # #CHATS PAGE TESTING
    # @patch("app.mongo")
    # def test_chat_page_loads_correctly(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     mock_user = {
    #         "_id": ObjectId(matched_user_id),
    #         "username": "testuser",
    #         "dob": "1999-01-01"
    #     }

    #     mock_mongo.db.users.find_one.side_effect = [mock_user]
    #     mock_mongo.db.messages.find.return_value = []

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get(f"/chat/{matched_user_id}")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(b"testuser", response.data)



    # @patch("app.mongo")
    # def test_message_is_sent_and_censored(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     mock_user = {"_id": ObjectId(matched_user_id), "username": "user2"}
    #     mock_mongo.db.users.find_one.side_effect = [mock_user, mock_user]
    #     mock_mongo.db.messages.find.return_value = []

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post(f"/chat/{matched_user_id}", json={"message": "You are a bitch"})
    #     data = response.get_json()
    #     self.assertTrue(data["success"])
    #     self.assertNotIn("bitch", data["text"])  # Censored



    # @patch("app.mongo")
    # def test_message_with_profanity_middle(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     mock_user = {"_id": ObjectId(matched_user_id), "username": "user2"}
    #     mock_mongo.db.users.find_one.side_effect = [mock_user, mock_user]
    #     mock_mongo.db.messages.find.return_value = []

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.post(f"/chat/{matched_user_id}", json={"message": "This film is shit"})
    #     data = response.get_json()
    #     self.assertTrue(data["success"])
    #     self.assertIn("s***", data["text"].lower())  # Partially censored


    # @patch("app.mongo")
    # def test_chat_messages_ajax_response(self, mock_mongo):
    #     fake_user_id = str(ObjectId())
    #     matched_user_id = str(ObjectId())

    #     mock_user = {"_id": ObjectId(matched_user_id), "username": "user2"}
    #     mock_messages = [{
    #         "sender": ObjectId(fake_user_id),
    #         "receiver": ObjectId(matched_user_id),
    #         "text": "Hello!",
    #         "timestamp": datetime.utcnow()
    #     }]

    #     mock_mongo.db.users.find_one.side_effect = [mock_user]
    #     mock_mongo.db.messages.find.return_value = mock_messages

    #     with self.app.session_transaction() as sess:
    #         sess["user_id"] = fake_user_id

    #     response = self.app.get(
    #         f"/chat/{matched_user_id}",
    #         headers={"X-Requested-With": "XMLHttpRequest"}
    #     )

    #     self.assertEqual(response.status_code, 200)

    #     # Parse the JSON and assert cleanly
    #     data = response.get_json()
    #     self.assertEqual(data["messages"][0]["text"], "Hello!")
    #     self.assertEqual(data["messages"][0]["sender_name"], "You")







if __name__ == '__main__':
    unittest.main()




#need to change 2 sets of the tests data when testing
