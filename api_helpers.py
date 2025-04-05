import requests
import time

def search_movies(query):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
        "query": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        movies = response.json()['results']
        return [{'id': movie['id'], 'title': movie['title']} for movie in movies]
    else:
        return []



def search_actors(query):
    url = "https://api.themoviedb.org/3/search/person"
    params = {
        "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
        "query": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        actors = response.json()['results']
        return [{'id': actor['id'], 'name': actor['name']} for actor in actors]
    else:
        return []



def search_genres(query):
    url = "https://api.themoviedb.org/3/genre/movie/list"
    params = {
        "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
        "language": "en-US"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        genres = response.json().get("genres", [])
        filtered_genres = [genre for genre in genres if query.lower() in genre["name"].lower()]
        return [{'id': genre['id'], 'name': genre['name']} for genre in filtered_genres]
    else:
        return []



# TMDB Genre Mapping (Name → ID)
GENRE_ID_MAP = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80,
    "Documentary": 99, "Drama": 18, "Family": 10751, "Fantasy": 14, "History": 36,
    "Horror": 27, "Music": 10402, "Mystery": 9648, "Romance": 10749, "Sci-Fi": 878,
    "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
}

def search_popular_movies_by_genre(genre_names=None, max_pages=20):
    """Fetches the most popular movies for given genres from TMDB API, sorted by popularity."""
    url = "https://api.themoviedb.org/3/discover/movie"
    all_movies = []  # Store all fetched movies

    # Convert Genre Names to TMDB Genre IDs
    genre_ids = [str(GENRE_ID_MAP.get(genre, "")) for genre in (genre_names or []) if genre in GENRE_ID_MAP]
    genre_query = ",".join(genre_ids) if genre_ids else "" 

    for page in range(1, max_pages + 1): 
        params = {
            "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
            "language": "en-US",
            "sort_by": "popularity.desc",  # Most popular first
            "with_genres": genre_query if genre_query else None,  # All movies if empty
            "page": page
        }

        for attempt in range(3):  
            response = requests.get(url, params=params)
            if response.status_code == 200:
                break  
            print(f"⚠️ API request failed (Attempt {attempt + 1}) - Status Code: {response.status_code}")
            time.sleep(1)  
        if response.status_code != 200:
            print(f" Failed to fetch movies for genres {genre_names}, page {page}")
            continue  
        movies = response.json().get("results", [])
        all_movies.extend([
            {
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                'popularity': movie.get("popularity", 0),  # Store popularity for sorting
                'genre': genre_names or ["All Genres"]  # Default to "All Genres" if None
            }
            for movie in movies
        ])
    all_movies = sorted(all_movies, key=lambda x: x["popularity"], reverse=True)
    return all_movies 

