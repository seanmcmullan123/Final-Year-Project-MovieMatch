
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import random
import json  
from werkzeug.utils import secure_filename
from api_helpers import search_movies, search_actors
from flask import jsonify
from flask import Flask, request, jsonify, redirect, url_for, flash, render_template
from bson.objectid import ObjectId
from api_helpers import search_movies, search_actors, search_genres, search_popular_movies_by_genre
from better_profanity import profanity
import re  # For email and password pattern checking
import base64
from PIL import Image
from io import BytesIO
from azure.storage.blob import ContentSettings


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB setup with Cosmos DB
app.config["MONGO_URI"] = "mongodb://moviematchcosmos:LZyCVl9nFRB1sDsONaQ1wykcPuKHVZEqj8IuxDZTCBTYENbzgbFKXPaY1Tux3mM1JxP3xVZwPcSmACDbJi8QlQ==@moviematchcosmos.mongo.cosmos.azure.com:10255/MovieMatchDB?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@moviematchcosmos@"
mongo = PyMongo(app)

# Azure Blob Storage setup
connect_str = "DefaultEndpointsProtocol=https;AccountName=moviematchstorageaccount;AccountKey=gEAdsvNVv6vQFalK32i3qBEYo5omHhJ+eNlxzs43cvs0lIYq0OPxaMUjpZTT9ZaoDb4ZlNZ+VTiN+ASt3eWVeA==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'user-profile-pics'
container_client = blob_service_client.get_container_client(container_name)



def calculate_age(birthdate):
    """Helper function to calculate age from a birthdate."""
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))



@app.route('/')
def home():
    return render_template('index.html')



profanity.load_censor_words()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        dob_str = request.form['dob']
        gender = request.form.get('gender')

        # Check all fields are filled
        if not username or not email or not password or not dob_str or not gender:
            flash("Please fill out all fields, including gender.", "danger")
            return redirect(url_for('register'))

        # Profanity check
        if profanity.contains_profanity(username) or profanity.contains_profanity(email) or profanity.contains_profanity(password):
            flash("Username, email, or password contains inappropriate language.", "danger")
            return redirect(url_for('register'))

        # Username: minimum 6 characters
        if len(username) < 6:
            flash("Username must be at least 6 characters long.", "danger")
            return redirect(url_for('register'))

        # Email: basic format + minimum 2 characters before '@' and valid domain
        if not re.match(r"^[\w\.-]{2,}@[\w\.-]+\.(com|net|org|co\.uk|ie|edu|gov|info|io)$", email):
            flash("Invalid email format. Please use a valid domain (e.g., gmail.com).", "danger")
            return redirect(url_for('register'))

        # Password: at least 8 characters and contains a number
        if len(password) < 8 or not re.search(r"\d", password):
            flash("Password must be at least 8 characters and contain a number.", "danger")
            return redirect(url_for('register'))

            # ✅ Confirm password matches
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))
                    
        # Age Check: Must be 18 or older
        try:
            dob_date = datetime.strptime(dob_str, '%Y-%m-%d')
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('register'))

        age = calculate_age(dob_date)
        if age < 18:
            flash("You must be at least 18 years old to register.", "danger")
            return redirect(url_for('register'))

        # Check if username or email already exists
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

        if mongo.db.users.find_one({"email": email}):
            flash("Email already exists.", "danger")
            return redirect(url_for('register'))

        # Get user_id
        user_id_counter = mongo.db.counters.find_one_and_update(
            {"id": "user_id"},
            {"$inc": {"sequence_value": 1}},
            new=True
        )

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        # Insert user into DB
        mongo.db.users.insert_one({
            "user_id": user_id_counter['sequence_value'],
            "username": username,
            "email": email,
            "password": hashed_password,
            "dob": dob_date,
            "gender": gender
        })
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', autocomplete='off')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #  NEW: Check if either field is blank
        if not username or not password:
            flash("Please fill in both fields", "danger")
            return redirect(url_for('login'))
        
        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash("Login successful!", "success")
            return redirect(url_for('profile'))
        else:
            flash("Invalid username or password. Please register if you haven't.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html', autocomplete='off')




@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully!", "info")
    return redirect(url_for('home'))  # Redirects to homepage




@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("You must be logged in to view your profile.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    movies = []
    actors = []
    age = "N/A"  # Default if DOB is missing
    gender = "Not Specified"  # Default if gender is missing
    gender_preference = "Both"  # Default if gender preference is missing

    try:
        if user:
            print("User Data from MongoDB:", user)

            user["fav_movies"] = user.get("fav_movies", [])
            user["fav_actors"] = user.get("fav_actors", [])
            user["fav_genres"] = user.get("fav_genres", [])
            user["gender"] = user.get("gender", "Not Specified")
            user["gender_preference"] = user.get("gender_preference", "Both")

            dob = user.get("dob")
            if dob:
                if isinstance(dob, str):
                    dob = datetime.strptime(dob, "%Y-%m-%d")
                age = datetime.now().year - dob.year - ((datetime.now().month, datetime.now().day) < (dob.month, dob.day))

            print("FINAL fav_movies:", user["fav_movies"])
            print("FINAL fav_actors:", user["fav_actors"])
            print("FINAL fav_genres:", user["fav_genres"])
            print("FINAL Gender:", user["gender"])
            print("FINAL Gender Preference:", user["gender_preference"])
            print("FINAL Age:", age)

        if request.method == 'POST':
            movie_query = request.form.get('movie_query')
            actor_query = request.form.get('actor_query')
            movies = search_movies(movie_query) if movie_query else []
            actors = search_actors(actor_query) if actor_query else []
        timestamp = datetime.utcnow().timestamp()

        return render_template(
            'profile.html',
            user=user,
            age=age,
            movies=movies,
            actors=actors,
            genres=user["fav_genres"],
            gender=user["gender"],
            gender_preference=user["gender_preference"],
            timestamp=timestamp 
        )

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while processing your request.", "error")
        return render_template(
            'profile.html',
            user=user,
            age=age,
            movies=[],
            actors=[],
            genres=[],
            gender="Not Specified",
            gender_preference="Both",
            timestamp=datetime.utcnow().timestamp()  
        )




@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    user_id = ObjectId(session['user_id'])

    # Delete user from users collection
    mongo.db.users.delete_one({"_id": user_id})

    # Remove user from matches, swipes, and messages
    mongo.db.swipes.delete_many({"user_id": user_id})
    mongo.db.matches.delete_many({"$or": [{"user_1": user_id}, {"user_2": user_id}]}) 
    mongo.db.messages.delete_many({"$or": [{"sender": user_id}, {"receiver": user_id}]})

    # Clear session
    session.clear()
    return jsonify({"success": True})




@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        flash("You must be logged in to edit your profile.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    # Ensure all fields exist and default to empty lists
    user["fav_movies"] = user.get("fav_movies", [])
    user["fav_actors"] = user.get("fav_actors", [])
    user["fav_genres"] = user.get("fav_genres", [])
    user["gender_preference"] = user.get("gender_preference", "Both")  # Default to "Both" if not set


    if request.method == 'POST':
        profile_pic_url = user.get("profile_pic_url")
        profile_pic_file = request.files.get('profile_pic')

        # Cropped image 
        cropped_data = request.form.get('cropped_image_data')
        if cropped_data:
            try:
                print("⚠️ Cropped image data received.")
                header, encoded = cropped_data.split(",", 1)
                decoded = base64.b64decode(encoded)
                image = Image.open(BytesIO(decoded))
                filename = f"{user_id}.jpg"
                blob_client = container_client.get_blob_client(blob=filename)

                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)

                # Upload to Azure Blob with content type set
                blob_client.upload_blob(
                    buffer.read(),
                    overwrite=True,
                    content_settings=ContentSettings(content_type='image/jpeg')
                )

                # Update the profile_pic_url
                profile_pic_url = f"https://moviematchstorageaccount.blob.core.windows.net/user-profile-pics/{filename}"
                print(" Uploaded cropped image to Azure:", profile_pic_url)
            except Exception as e:
                print(" Cropped image upload failed:", e)
                flash(f"Error processing cropped image: {str(e)}", "danger")
        elif profile_pic_file:
            try:
                filename = f"{user_id}.jpg"
                blob_client = container_client.get_blob_client(blob=filename)
                blob_client.upload_blob(
                    profile_pic_file.read(),
                    overwrite=True,
                    content_settings=ContentSettings(content_type='image/jpeg')
                )
                profile_pic_url = f"https://moviematchstorageaccount.blob.core.windows.net/user-profile-pics/{filename}"
                print(" Uploaded standard profile image to Azure:", profile_pic_url)
            except Exception as e:
                print(" Standard image upload failed:", e)
                flash(f"Error uploading image: {str(e)}", "danger")

        username = request.form.get('username', '').strip()
        bio = request.form.get('bio', '').strip()
        fun_fact = request.form.get('fun_fact', '').strip()
        gender_preference = request.form.get('gender_preference', 'Both').strip()

        # Username validation
        if len(username) < 6:
            flash("Username must be at least 6 characters long.", "danger")
            return redirect(url_for('edit_profile'))

        if profanity.contains_profanity(username):
            flash("Username contains inappropriate language.", "danger")
            return redirect(url_for('edit_profile'))

        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user and str(existing_user["_id"]) != user_id:
            flash("Username already taken. Please choose another.", "danger")
            return redirect(url_for('edit_profile'))

        # Bio validation
        if len(bio) < 6:
            flash("Bio must be at least 6 characters long.", "danger")
            return redirect(url_for('edit_profile'))

        if profanity.contains_profanity(bio):
            flash("Bio contains inappropriate language.", "danger")
            return redirect(url_for('edit_profile'))

        # Fun fact validation
        if len(fun_fact) < 6:
            flash("Fun Fact must be at least 6 characters long.", "danger")
            return redirect(url_for('edit_profile'))

        if profanity.contains_profanity(fun_fact):
            flash("Fun Fact contains inappropriate language.", "danger")
            return redirect(url_for('edit_profile'))

        # Detect empty lists
        fav_movies = request.form.get("fav_movies", "[]").strip()
        fav_actors = request.form.get("fav_actors", "[]").strip()
        fav_genres = request.form.get("fav_genres", "[]").strip()

        try:
            fav_movies = json.loads(fav_movies) if fav_movies else []
            fav_actors = json.loads(fav_actors) if fav_actors else []
            fav_genres = json.loads(fav_genres) if fav_genres else []
        except json.JSONDecodeError:
            fav_movies, fav_actors, fav_genres = [], [], []

        # Valid format and enforce limits
        fav_movies = [m.strip() for m in fav_movies if m.strip()][:3]
        fav_actors = [a.strip() for a in fav_actors if a.strip()][:3]
        fav_genres = [g.strip() for g in fav_genres if g.strip()][:5]

        update_data = {
            "username": username,
            "bio": bio,
            "fun_fact": fun_fact,
            "fav_movies": fav_movies,
            "fav_actors": fav_actors,
            "fav_genres": fav_genres,
            "profile_pic_url": profile_pic_url,
            "gender_preference": gender_preference 
        }
        print(" DEBUG - Final Data to Save:", update_data)  # Debugging logs

        mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        flash("Profile updated successfully!", "success")
        return redirect(url_for('edit_profile'))

    existing_movies = user.get("fav_movies", [])
    existing_actors = user.get("fav_actors", [])
    existing_genres = user.get("fav_genres", [])
    existing_gender_preference = user.get("gender_preference", "Both")  

    return render_template(
    "profile_edit.html",
    user=user,
    movies=existing_movies,
    actors=existing_actors,
    genres=existing_genres,
    gender_preference=existing_gender_preference, 
    timestamp=datetime.utcnow().timestamp()        
)




# Search routes for AJAX calls
@app.route('/search/movies', methods=['GET'])
def ajax_search_movies():
    query = request.args.get('query', '')
    if query:
        return jsonify(search_movies(query))
    return jsonify([])


@app.route('/search/actors', methods=['GET'])
def ajax_search_actors():
    query = request.args.get('query', '')
    if query:
        return jsonify(search_actors(query))
    return jsonify([])


@app.route('/search/genres', methods=['GET'])
def ajax_search_genres():
    query = request.args.get('query', '')
    if query:
        return jsonify(search_genres(query))
    return jsonify([])





@app.route('/swipe_movies', methods=['GET', 'POST'])
def swipe_movies():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    user = mongo.db.users.find_one({"_id": user_id})


    # Fetch matches where current user is involved
    all_matches = list(mongo.db.matches.find({
        "$or": [{"user_1": user_id}, {"user_2": user_id}]
    }))
    valid_match_count = 0

    for match in all_matches:
        other_user_id = match["user_2"] if match["user_1"] == user_id else match["user_1"]

        # If the other user doesn't exist, REMOVE the match from the DB
        if not mongo.db.users.find_one({"_id": other_user_id}):
            mongo.db.matches.delete_one({"_id": match["_id"]})  # Remove invalid match
        else:
            valid_match_count += 1  # Count only active matches
    matches_count = valid_match_count

    # Ensure user profile is complete before swiping
    if not (user.get('bio') and user.get('fun_fact') and user.get('profile_pic_url')):
        flash("Complete your profile to proceed.", "danger")
        return redirect(url_for('edit_profile'))

    user_gender = user.get("gender", "")
    user_gender_preference = user.get("gender_preference", "Both")  # Default to "Both"

    # Handle POST Request (User Swiped Movie)
    if request.method == 'POST':
        data = request.get_json()
        movie_id = data.get("movie_id")
        action = data.get("action")  # 'like' or 'dislike'
        if not movie_id or action not in ['like', 'dislike']:
            return jsonify({"success": False, "error": "Invalid swipe data"}), 400

        # Store swipe action in MongoDB
        mongo.db.user_swipes.insert_one({
            "user_id": user_id,
            "movie_id": movie_id,
            "action": action
        })

        # Matching Algorithm: Find users who liked the same movies (Only match if 10+ movies match)
        if action == 'like':
            matched_users = list(mongo.db.user_swipes.find({
                "movie_id": movie_id,
                "action": "like",
                "user_id": {"$ne": user_id}
            }))

            for match in matched_users:
                matched_user_id = match["user_id"]
                matched_user = mongo.db.users.find_one({"_id": ObjectId(matched_user_id)})
                if not matched_user:
                    continue  # Skip if user is not found

                matched_gender = matched_user.get("gender", "")
                matched_gender_preference = matched_user.get("gender_preference", "Both")

                # Ensure BOTH users match each other's gender preference
                gender_match = (
                    (user_gender_preference == "Both" or user_gender_preference == matched_gender) and
                    (matched_gender_preference == "Both" or matched_gender_preference == user_gender)
                )

                if not gender_match:
                    continue  # Skip this match if gender preferences do not align

                # Get movies both users have liked
                user_liked_movies = set(swipe["movie_id"] for swipe in mongo.db.user_swipes.find({
                    "user_id": user_id, "action": "like"
                }))
                matched_user_liked_movies = set(swipe["movie_id"] for swipe in mongo.db.user_swipes.find({
                    "user_id": matched_user_id, "action": "like"
                }))

                #  Find common liked movies
                common_movies = user_liked_movies.intersection(matched_user_liked_movies)
                common_movies_count = len(common_movies)

                print(f"DEBUG: {user_id} & {matched_user_id} - Common Movies: {common_movies_count}")

                # Only match if they have at least 10 movies in common
                if common_movies_count >= 10:
                    existing_match = mongo.db.matches.find_one({
                        "$or": [
                            {"user_1": user_id, "user_2": matched_user_id},
                            {"user_1": matched_user_id, "user_2": user_id}
                        ]
                    })

                    #  Ensure match is NOT already in the database
                    if existing_match:
                        print(f"DEBUG: Match already exists for {user_id} & {matched_user_id}")
                    else:
                        print(f" MATCH CREATED: {user_id} & {matched_user_id} - {common_movies_count} common likes")

                        mongo.db.matches.insert_one({
                            "user_1": user_id,
                            "user_2": matched_user_id,
                            "common_likes": common_movies_count
                        })
        return jsonify({"success": True})  # Send success response

    # GET Request
    selected_genres = user.get('fav_genres', [])  # Ensure it's a list

    # Fetch "Most Popular" Movies from TMDB
    movies_list = []
    if selected_genres:
        movies_list = search_popular_movies_by_genre(selected_genres, max_pages=20)  
    else:
        movies_list = search_popular_movies_by_genre([], max_pages=20)  # All movies

    print(f" Total Popular Movies Fetched: {len(movies_list)}")  # Debugging Output

    # Remove movies the user already swiped
    swiped_movie_ids = {swipe["movie_id"] for swipe in mongo.db.user_swipes.find({"user_id": user_id})}
    movies_list = [movie for movie in movies_list if str(movie["id"]) not in swiped_movie_ids]

    print(f" Movies Remaining After Removing Swiped: {len(movies_list)}")  # Debugging Output

    # Sort the first 20 movies by popularity (highest first)
    movies_list = sorted(movies_list, key=lambda x: x.get("popularity", 0), reverse=True)

    # Over 20 movies are left then shuffle 
    if len(movies_list) > 20:
        top_20_movies = movies_list[:20]  # Keep the first 20 in order
        remaining_movies = movies_list[20:]  # Shuffle the rest
        random.shuffle(remaining_movies)
        movies_list = top_20_movies + remaining_movies

    if not movies_list:
        print(" All movies swiped! Resetting swipe history and fetching new ones.")
        mongo.db.user_swipes.delete_many({"user_id": user_id})  # Clear history
        movies_list = search_popular_movies_by_genre(selected_genres if selected_genres else [], max_pages=20)

    # Select the first movie to show
    movie_to_show = movies_list[0] if movies_list else None

    matches_count = mongo.db.matches.count_documents({
        "$or": [{"user_1": ObjectId(user_id)}, {"user_2": ObjectId(user_id)}]
    })
    return render_template('swipe_movies.html', movie=movie_to_show, genres=selected_genres, matches_count=matches_count)





@app.route('/swipe_action', methods=['POST'])
def swipe_action():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "User not logged in."})

    user_id = session['user_id']
    movie_id = request.args.get("movie_id")
    action = request.args.get("action")  # "like" or "dislike"

    if not movie_id or not action:
        return jsonify({"success": False, "message": "Invalid request."})

    # Store swipe action in MongoDB
    mongo.db.swipes.update_one(
        {"user_id": ObjectId(user_id), "movie_id": ObjectId(movie_id)},
        {"$set": {"action": action}},
        upsert=True  
    )
    return jsonify({"success": True})





@app.route('/matches', methods=['GET'])
def view_matches():
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    user = mongo.db.users.find_one({"_id": user_id})

    user_gender = user.get("gender")
    gender_preference = user.get("gender_preference")

    # Fetch all matches involving the current user
    matches = list(mongo.db.matches.find({
        "$or": [{"user_1": user_id}, {"user_2": user_id}]
    }))
    filtered_matches = []
    for match in matches:
        matched_user_id = match["user_1"] if match["user_2"] == user_id else match["user_2"]
        matched_user = mongo.db.users.find_one({"_id": matched_user_id})

        if matched_user:
            matched_gender = matched_user.get("gender")

            # Gender preference filter
            if gender_preference == "Male" and matched_gender != "Male":
                continue
            if gender_preference == "Female" and matched_gender != "Female":
                continue

            filtered_matches.append({
                "user_id": str(matched_user["_id"]),  
                "username": matched_user.get("username"),
                "profile_pic_url": matched_user.get("profile_pic_url"),
                "common_likes": match.get("common_likes")
            })
    return render_template('matches.html', matches=filtered_matches)





@app.route('/remove_match', methods=['POST'])
def remove_match():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    data = request.get_json()
    matched_user_id = data.get("matched_user_id")

    if not matched_user_id:
        return jsonify({"success": False, "error": "Missing matched user ID"}), 400

    user_id = ObjectId(session['user_id'])
    matched_user_id = ObjectId(matched_user_id)

    # Remove the match from either direction
    result = mongo.db.matches.delete_one({
        "$or": [
            {"user_1": user_id, "user_2": matched_user_id},
            {"user_1": matched_user_id, "user_2": user_id}
        ]
    })
    if result.deleted_count > 0:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Match not found"}), 404





@app.route('/match_profile/<user_id>', methods=['GET'])
def view_match_profile(user_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    matched_user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not matched_user:
        flash("User profile not found.", "danger")
        return redirect(url_for('view_matches'))
    return render_template('match_profile.html', user=matched_user)





UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load profanity but blur all letters after first
profanity.load_censor_words()

def custom_censor_text(message):
    words = message.split()
    censored_words = []
    for word in words:
        cleaned = re.sub(r'[^\w]', '', word).lower()  # Strip punctuation
        if profanity.contains_profanity(cleaned):
            censored = word[0] + '*' * (len(word) - 1)
            censored_words.append(censored)
        else:
            censored_words.append(word)
    return ' '.join(censored_words)





@app.route('/chat/<matched_user_id>', methods=['GET', 'POST'])
def chat(matched_user_id):
    if 'user_id' not in session:
        flash("You need to log in first.", "danger")
        return redirect(url_for('login'))

    user_id = ObjectId(session['user_id'])
    matched_user = mongo.db.users.find_one({"_id": ObjectId(matched_user_id)})

    age = None
    dob = matched_user.get("dob")
    if dob:
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%Y-%m-%d")
        age = datetime.now().year - dob.year - ((datetime.now().month, datetime.now().day) < (dob.month, dob.day))


    if not matched_user:
        flash("User not found.", "danger")
        return redirect(url_for('view_matches'))

    messages = list(mongo.db.messages.find({
        "$or": [
            {"sender": user_id, "receiver": ObjectId(matched_user_id)},
            {"sender": ObjectId(matched_user_id), "receiver": user_id}
        ]
    }))
    for message in messages:
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow()
            mongo.db.messages.update_one(
                {"_id": message["_id"]},
                {"$set": {"timestamp": message["timestamp"]}}
            )
    messages = sorted(messages, key=lambda x: x["timestamp"])
    for message in messages:
        message["sender"] = str(message["sender"])
        message["receiver"] = str(message["receiver"])

    # return JSON instead of HTML
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "messages": [
                {
                    "sender": msg["sender"],
                    "receiver": msg["receiver"],
                    "text": msg["text"],
                    "sender_name": "You" if msg["sender"] == str(user_id) else matched_user["username"]
                }
                for msg in messages
            ]
        })
  


    if request.method == 'POST':
        data = request.get_json()
        message_text = data.get("message", "").strip()

        if not message_text:
            return jsonify({"success": False, "error": "Message cannot be empty"}), 400

        censored_text = custom_censor_text(message_text)
        new_message = {
            "sender": user_id,
            "receiver": ObjectId(matched_user_id),
            "text": censored_text,
            "timestamp": datetime.utcnow()
        }
        mongo.db.messages.insert_one(new_message)
        return jsonify({"success": True, "text": censored_text, "sender": str(user_id)})
    return render_template('chat.html', matched_user=matched_user, messages=messages, current_user_id=str(user_id), age=age)



# TODO: Changed this to allow all exposure on all dns entries
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


