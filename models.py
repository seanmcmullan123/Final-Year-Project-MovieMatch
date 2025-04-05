# from datetime import datetime
# from pymongo import MongoClient

# # Your MongoDB connection string
# client = MongoClient('mongodb://moviematchcosmos:LZyCVl9nFRB1sDsONaQ1wykcPuKHVZEqj8IuxDZTCBTYENbzgbFKXPaY1Tux3mM1JxP3xVZwPcSmACDbJi8QlQ==@moviematchcosmos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@moviematchcosmos@')
# db = client['MovieMatchDB']

# def calculate_age(birthdate):
#     """Helper function to calculate age from a birthdate."""
#     today = datetime.today()
#     return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# class User:
#     def __init__(self, username, email, password, dob, profile_pic_url=None, bio=None, fun_fact=None, fav_movies=None, fav_actors=None):
#         self.username = username
#         self.email = email
#         self.password = password  # Remember to hash passwords in production
#         self.dob = dob
#         self.profile_pic_url = profile_pic_url
#         self.bio = bio
#         self.fun_fact = fun_fact
#         self.fav_movies = fav_movies
#         self.fav_actors = fav_actors

#     def save(self):
#         """Save user to MongoDB."""
#         user_collection = db.users
#         user_dict = self.__dict__
#         user_collection.insert_one(user_dict)

# class Movie:
#     def __init__(self, title, genre, description, image_url):
#         self.title = title
#         self.genre = genre
#         self.description = description
#         self.image_url = image_url

#     def save(self):
#         """Save movie to MongoDB."""
#         movie_collection = db.movies
#         movie_dict = self.__dict__
#         movie_collection.insert_one(movie_dict)

# def add_movie_option(title):
#     movie_option_collection = db.movie_options
#     movie_option_collection.insert_one({"title": title})

# def add_actor_option(name):
#     actor_option_collection = db.actor_options
#     actor_option_collection.insert_one({"name": name})
