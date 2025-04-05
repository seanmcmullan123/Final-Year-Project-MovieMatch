
# seed_data.py
from pymongo import MongoClient

# MongoDB connection string
client = MongoClient("mongodb://moviematchcosmos:LZyCVl9nFRB1sDsONaQ1wykcPuKHVZEqj8IuxDZTCBTYENbzgbFKXPaY1Tux3mM1JxP3xVZwPcSmACDbJi8QlQ==@moviematchcosmos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@moviematchcosmos@")
db = client["MovieMatchDB"]  # Your database name

def seed_movie_options():
    """Add a few movies to the database, if they don't already exist."""
    movie_titles = [
        "Inception", "Titanic", "Avatar", "The Dark Knight",
        "Avengers: Endgame", "Pulp Fiction"
        # ... (expand this list with thousands more if needed)
    ]
    movies_collection = db["movies"]  # Your collection name for movies
    for title in movie_titles:
        # Check if it already exists
        if not movies_collection.find_one({"title": title}):
            movies_collection.insert_one({"title": title})

def seed_actor_options():
    """Add a few actors to the database, if they don't already exist."""
    actor_names = [
        "Tom Hanks", "Natalie Portman", "Denzel Washington",
        "Leonardo DiCaprio", "Meryl Streep"
        # ... (expand this list with thousands more if needed)
    ]
    actors_collection = db["actors"]  # Your collection name for actors
    for name in actor_names:
        if not actors_collection.find_one({"name": name}):
            actors_collection.insert_one({"name": name})

if __name__ == '__main__':
    seed_movie_options()
    seed_actor_options()
    print("Seeding complete!")


 