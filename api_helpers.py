# api_helpers.py
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




# # ✅ TMDB Genre Mapping (Name → ID)
# GENRE_ID_MAP = {
#     "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80,
#     "Documentary": 99, "Drama": 18, "Family": 10751, "Fantasy": 14, "History": 36,
#     "Horror": 27, "Music": 10402, "Mystery": 9648, "Romance": 10749, "Sci-Fi": 878,
#     "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
# }

# def search_popular_movies_by_genre(genre_names, max_pages=20):  # ✅ Fix: Added max_pages as a parameter
#     url = "https://api.themoviedb.org/3/discover/movie"
#     all_movies = []  # ✅ Store all fetched movies

#     # ✅ Convert Genre Names to TMDB Genre IDs
#     genre_ids = [str(GENRE_ID_MAP.get(genre, "")) for genre in genre_names if genre in GENRE_ID_MAP]
#     genre_query = ",".join(genre_ids) if genre_ids else ""

#     for page in range(1, max_pages + 1):  # ✅ Use max_pages parameter
#         params = {
#             "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
#             "language": "en-US",
#             "sort_by": "popularity.desc",  # ✅ Most popular first
#             "with_genres": genre_query,  # ✅ Use genre IDs in API request
#             "page": page  # ✅ Get different pages
#         }

#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             movies = response.json().get("results", [])
#             all_movies.extend([
#                 {
#                     'id': movie['id'],
#                     'title': movie['title'],
#                     'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
#                     'genre': genre_names  # ✅ Store genre names for reference
#                 }
#                 for movie in movies
#             ])
#         else:
#             print(f"⚠️ Failed to fetch movies for genres {genre_names}, page {page}")

#     return all_movies  # ✅ Return large movie list









# ✅ TMDB Genre Mapping (Name → ID)
GENRE_ID_MAP = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80,
    "Documentary": 99, "Drama": 18, "Family": 10751, "Fantasy": 14, "History": 36,
    "Horror": 27, "Music": 10402, "Mystery": 9648, "Romance": 10749, "Sci-Fi": 878,
    "TV Movie": 10770, "Thriller": 53, "War": 10752, "Western": 37
}

def search_popular_movies_by_genre(genre_names=None, max_pages=20):
    """Fetches the most popular movies for given genres from TMDB API, sorted by popularity."""
    
    url = "https://api.themoviedb.org/3/discover/movie"
    all_movies = []  # ✅ Store all fetched movies

    # ✅ Convert Genre Names to TMDB Genre IDs
    genre_ids = [str(GENRE_ID_MAP.get(genre, "")) for genre in (genre_names or []) if genre in GENRE_ID_MAP]
    genre_query = ",".join(genre_ids) if genre_ids else ""  # ✅ Support all movies if genre_names is None

    for page in range(1, max_pages + 1):  # ✅ Use max_pages parameter
        params = {
            "api_key": "6edf1358bfe4a6d2f35db741ee24c3c1",
            "language": "en-US",
            "sort_by": "popularity.desc",  # ✅ Most popular first
            "with_genres": genre_query if genre_query else None,  # ✅ Fetch all movies if empty
            "page": page
        }

        for attempt in range(3):  # ✅ Retry logic (up to 3 attempts)
            response = requests.get(url, params=params)
            if response.status_code == 200:
                break  # ✅ Success, exit retry loop
            print(f"⚠️ API request failed (Attempt {attempt + 1}) - Status Code: {response.status_code}")
            time.sleep(1)  # ✅ Short delay before retrying

        if response.status_code != 200:
            print(f"❌ Failed to fetch movies for genres {genre_names}, page {page}")
            continue  # ✅ Skip this page if API fails completely

        movies = response.json().get("results", [])
        all_movies.extend([
            {
                'id': movie['id'],
                'title': movie['title'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                'popularity': movie.get("popularity", 0),  # ✅ Store popularity for sorting
                'genre': genre_names or ["All Genres"]  # ✅ Default to "All Genres" if None
            }
            for movie in movies
        ])

    # ✅ Ensure movies are sorted by popularity (TMDB already sorts them, but just in case)
    all_movies = sorted(all_movies, key=lambda x: x["popularity"], reverse=True)

    return all_movies  # ✅ Return large sorted movie list
