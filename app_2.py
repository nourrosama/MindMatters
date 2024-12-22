from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime 
import secrets
from authlib.integrations.flask_client import OAuth
from bson import ObjectId
from flask_pymongo import PyMongo
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key

## MongoDB Configuration
#app.config["MONGO_URI"] = "mongodb://localhost:27017/MindMatters"
#mongo = PyMongo(app)

# Initialize MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["MindMatters"]  # Replace with your actual database name

# Collections
users_collection = db['Users']
journals_collection = db['JournalEntries']
consultations_collection = db['Consultations']
surveys_collection = db['Surveys']
forum_posts_collection = db['ForumPosts']
notifications_collection = db['Notifications']
resources_collection = db['Resources']
professionals_collection = db['Professionals']
bookings_collection = db['Bookings']
analysis_collection = db['Analysis']

## Update posts missing `createdAt`
#forum_posts_collection.update_many(
#    {"createdAt": {"$exists": False}},  # Find documents without `createdAt`
#    {"$set": {"createdAt": datetime.utcnow()}}  # Set default value
#)

# Test route to get all users
@app.route("/users", methods=["GET"])
def get_users():
    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string for JSON response
#    return jsonify(users)

# Route to add a new user
@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    data["createdAt"] = datetime.datetime.utcnow()
    data["updatedAt"] = datetime.datetime.utcnow()
    inserted = users_collection.insert_one(data)
    return jsonify({"message": "User added", "id": str(inserted.inserted_id)})


# Generate a random 32-byte string and encode it in hexadecimal
secure_key = secrets.token_hex(32)
app = Flask(__name__)
app.secret_key =  secure_key # For session management

# Initialize OAuth
oauth = OAuth(app)

# Google OAuth configuration
google = oauth.register(
    name='google',
    client_id='your_google_client_id',
    client_secret='your_google_client_secret',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)

# Facebook OAuth configuration
facebook = oauth.register(
    name='facebook',
    client_id='your_facebook_app_id',
    client_secret='your_facebook_app_secret',
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={'scope': 'email'}
)


@app.route("/feed", methods=["GET", "POST"])
def feed():
    user_email = session.get("user")  # Get the user from the session
    if not user_email:
        return redirect(url_for("login"))  # Redirect to login if not logged in

    user = users_collection.find_one({"email": user_email})  # Fetch user from MongoDB
    if user:
        if request.method == "POST":
            post_content = request.form.get("post_content")
            if post_content and post_content.strip():
                new_post = {
                    "username": user["username"],
                    "content": post_content.strip(),
                    "likes": 0,
                    "createdAt": datetime.utcnow()
                }
                forum_posts_collection.insert_one(new_post)  # Insert new post into MongoDB

        # Fetch all posts sorted by likes (desc), then by creation time (desc)
        posts = list(forum_posts_collection.find().sort([("likes", -1), ("createdAt", -1)]))
        
        return render_template("feed.html", username=user["username"], posts=posts)

    return redirect(url_for("login"))

# Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("signup.html")

        existing_user = users_collection.find_one({"email": email})
        hashed_password = generate_password_hash(password)

        if existing_user:
            flash("Email is already registered. Please log in.", "info")
            return redirect(url_for("login"))
        else:
            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": hashed_password,
                "role": "regular",
                "profile": {
                    "createdAt": datetime.utcnow(),
                    "updatedAt": datetime.utcnow(),
                }
            })
            flash("Signup successful! Please log in to continue.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html")

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user"] = email  # Store session
            flash("Login successful!", "success")
            return redirect(url_for("feed"))
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

    return render_template("login.html")

# Home Route
@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("feed"))
    return render_template("mainpage.html")

#Oauth
@app.route("/login/google")
def login_google():
    return google.authorize_redirect(url_for("authorize_google", _external=True))

@app.route("/authorize/google")
def authorize_google():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    
    session['user'] = {
        'provider': 'Google',
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'picture': user_info.get('picture')
    }


    return redirect(url_for("feed")) 

@app.route("/login/facebook")
def login_facebook():
    return facebook.authorize_redirect(url_for("authorize_facebook", _external=True))

@app.route("/authorize/facebook")
def authorize_facebook():
    token = facebook.authorize_access_token()
    user_info = facebook.get('me?fields=id,name,email,picture').json()



    return redirect(url_for("feed"))  

@app.route("/like_post/<string:post_id>", methods=["GET", "POST"])
def like_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]

    # Find the post by ID
    post = forum_posts_collection.find_one({"_id": ObjectId(post_id)})

    if post:
        # Initialize the `likes_tracking` field if it doesn't exist
        if "likes_tracking" not in post:
            post["likes_tracking"] = []

        # Check if the user has already liked the post
        if user_email in post["likes_tracking"]:
            flash("You can only like a post once.", "warning")
        else:
            # Add the user's email to the `likes_tracking` list and increment the like count
            forum_posts_collection.update_one(
                {"_id": ObjectId(post_id)},
                {
                    "$addToSet": {"likes_tracking": user_email},
                    "$inc": {"likes": 1}
                }
            )
            flash("Post liked!", "success")
    else:
        flash("Post not found.", "danger")

    return redirect(url_for("feed"))


@app.route("/comment_post/<string:post_id>", methods=["POST"])
def comment_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))
    comment_content = request.form.get("comment_content")
    user_email = session["user"]

    # Find the user by email
    user = users_collection.find_one({"email": user_email})

    if user and comment_content.strip():
        comment = {
            "username": user["username"],
            "content": comment_content.strip(),
            "createdAt": datetime.utcnow()
        }

        # Add the comment to the `comments` field in the post
        forum_posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$push": {"comments": comment}}
        )
        flash("Comment added!", "success")
    else:
        flash("Unable to add comment.", "danger")

    return redirect(url_for("feed"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get the logged-in user's email from the session
    user_email = session["user"]
    user = users_collection.find_one({"email": user_email})

    if user:
        # Prepare user data
        profile_data = user.get("profile", {})
        created_at = profile_data.get("createdAt")
        updated_at = profile_data.get("updatedAt")

        user_data = {
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role", "regular"),  # Default role as 'regular' if not found
            "profile_created_at": created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else None,
            
            "profile_updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_at else None,
            
            "bio": user.get("bio", "Welcome to my profile!"),

        }

        return render_template("profile.html", user=user_data)
    else:
        return redirect(url_for('login'))
    

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session["user"]
    user = users_collection.find_one({"email": user_email})

    if user:
        if request.method == "POST":
            bio = request.form.get("bio")
            avatar_url = request.form.get("avatar_url")

            # Update user profile data
            users_collection.update_one(
                {"email": user_email},
                {
                    "$set": {
                        "bio": bio,
                        "avatar_url": avatar_url,
                        "profile.updatedAt": datetime.utcnow()
                    }

                }
            )
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))

        return render_template("edit_profile.html", user=user)
    else:
        return redirect(url_for('login'))
    


@app.route("/consultation", methods=["GET"])
def consultation():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch all professionals from the Professionals collection
    all_doctors = professionals_collection.find()
    doctors = []

    for professional in all_doctors:
        doctors.append({
            "id": str(professional["_id"]),
            "name": professional.get("name", "Unknown"),
            "specialty": professional.get("specialty", "N/A"),
            "image": professional.get("image", "/static/images/default_profile.png"),
            "description": professional.get("description", "No description available."),
        })

    return render_template("consultation.html", doctors=doctors)

# View all bookings for the logged-in user
@app.route("/bookings", methods=["GET"])
def bookings():
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    user = users_collection.find_one({"email": user_email})

    if not user:
        return redirect(url_for("login"))

    # Aggregate user bookings with professional details
    user_bookings = bookings_collection.aggregate([
        {"$match": {"userId": ObjectId(user["_id"])}},
        {
            "$lookup": {
                "from": "Professionals",
                "localField": "professionalId",
                "foreignField": "_id",
                "as": "professionalDetails"
            }
        }
    ])

    # Convert cursor to list for rendering
    bookings_list = []
    for booking in user_bookings:
        professional = booking["professionalDetails"][0] if booking["professionalDetails"] else {}
        bookings_list.append({
            "id": str(booking["_id"]),
            "dateTime": booking["dateTime"],
            "status": booking["status"],
            "notes": booking.get("notes", ""),
            "professionalName": professional.get("name", "Unknown"),
            "professionalSpecialty": professional.get("specialty", "N/A"),
        })

    return render_template("booking.html", doctor=professional, bookings=bookings_list)

# Booking page for a specific professional
@app.route("/booking/<string:professional_id>", methods=["GET", "POST"])
def booking(professional_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    user = users_collection.find_one({"email": user_email})

    if not user:
        flash("User not found. Please log in again.", "danger")
        return redirect(url_for("login"))

    professional = professionals_collection.find_one({"_id": ObjectId(professional_id)})

    if not professional:
        flash("Professional not found.", "danger")
        print(f"No professional found with ID: {professional_id}")
        return redirect(url_for("consultation"))
    
    if request.method == "POST":
        date_time_str = request.form.get("dateTime")
        notes = request.form.get("notes")

        try:
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Invalid date or time format.", "danger")
            return redirect(url_for("booking", professional_id=professional_id))

        new_booking = {
            "userId": user["_id"],
            "professionalId": professional["_id"],
            "dateTime": date_time,
            "status": "pending",
            "notes": notes,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        bookings_collection.insert_one(new_booking)
        
          # Update the professional collection
        professionals_collection.update_one(
            {"_id": ObjectId(professional_id)},
            {
                "$inc": {"bookingCount": 1},  # Increment booking count by 1
                "$set": {"lastBookingDate": date_time},  # Update the last booking date
            }
        )

        flash("Appointment booked successfully!", "success")
        return redirect(url_for("bookings"))

    return render_template("booking.html", doctor=professional)
# not work aaccording to the database

# @app.route('/save', methods=['POST'])
# def save_entry():
#     mood = request.form.get('mood')
#     reflections = request.form.get('reflections')
#     tags = request.form.getlist('tags')

#     new_entry = {
#         "mood": mood,
#         "reflections": reflections,
#         "tags": tags,
#         "createdAt": datetime.utcnow(),
#         "updatedAt": datetime.utcnow(),
#     }
#     journals_collection.insert_one(new_entry)
#     return redirect(url_for("profile"))

# @app.route('/update', methods=['POST'])
# def update_mood():
#     data = request.json
#     user_id = data.get("userId")
#     mood_entry = {
#         "date": {"$date": data.get("date")},
#         "mood": data.get("mood")
#     }

#     result = analysis_collection.update_one(
#         {"userId": ObjectId(user_id)},
#         {"$push": {"moodData": mood_entry}, "$set": {"updatedAt": datetime.now()}},
#         upsert=True
#     )
#     return jsonify({"success": True, "matched_count": result.matched_count, "modified_count": result.modified_count})

# @app.route('/get_mood_graph/<user_id>', methods=['GET'])
# def get_mood_graph(user_id):
#     user_data = analysis_collection.find_one({"userId": ObjectId(user_id)})

#     if not user_data or 'moodData' not in user_data:
#         return jsonify({"error": "No mood data found for this user."}), 404

#     mood_data = user_data['moodData']

#     # Send the mood data as JSON for the frontend
#     return jsonify({
#         "success": True,
#         "moodData": mood_data
#     })
@app.route('/save', methods=['POST'])
def save_entry():
    # Collect form data
    mood = request.form.get('mood')
    reflections = request.form.get('reflections')
    tags = request.form.getlist('tags')  # Assuming a multiselect field for tags

    # Create a new journal entry
    new_entry = {
        "mood": mood,
        "reflections": reflections,
        "tags": tags,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    journals_collection.insert_one(new_entry)
    return redirect(url_for("profile"))

@app.route('/update', methods=['POST'])
def update_mood():
    data = request.json
    user_id = data.get("userId")
    mood_entry = {
        "date": {"$date": data.get("date")},
        "mood": data.get("mood")
    }

    # Update or insert mood data
    result = analysis_collection.update_one(
        {"userId": ObjectId(user_id)},
        {"$push": {"moodData": mood_entry}, "$set": {"updatedAt": datetime.datetime.now()}},
        upsert=True
    )
    return jsonify({"success": True, "matched_count": result.matched_count, "modified_count": result.modified_count})

@app.route('/get_mood_graph/<user_id>', methods=['GET'])
def get_mood_graph(user_id):
    # Fetch mood data for the user
    user_data = analysis_collection.find_one({"userId": ObjectId(user_id)})

    if not user_data or 'moodData' not in user_data:
        return jsonify({"error": "No mood data found for this user."}), 404

    # Extract dates and moods from the database
    dates = [entry['date'] for entry in user_data['moodData']]
    moods = [entry['mood'] for entry in user_data['moodData']]

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, moods, marker='o', color='b', linestyle='-', label="Mood")
    plt.title(f'Mood Trend for User {user_id}')
    plt.xlabel('Date')
    plt.ylabel('Mood')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show the plot (this will display it in the local environment)
    plt.show()

    return jsonify({"success": True, "message": "Graph displayed successfully."})

@app.route('/exercise')
def exercise():
    return render_template('exercies.html')

@app.route('/mood_tracking')
def mood_tracking():
    return render_template('mood_tracking.html')

@app.route('/services')
def services():
    return render_template('services.html')  

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return render_template('mainpage.html')

@app.route("/mood_analysis")
def mood_analysis():
    return render_template('mood_analysis.html')


@app.route("/resources")
def resources():
    return render_template("resources.html")

@app.route("/messages")
def messages():
    return render_template("messages.html")

@app.route("/trigger-404")
def trigger_404():
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
