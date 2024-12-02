from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime  
app = Flask(__name__)
app.secret_key = "your_secret_key"  # For session management

# In-memory database for users (use a real database in production)
users_db = {
    "user1@example.com": {"username": "user1", "password": "password123"},
    "user2@example.com": {"username": "user2", "password": "password456"}
}

# Preloaded posts for demonstration
posts_db = [
    {
        "id": 1,
        "username": "user1",
        "content": "Hello, world! This is my first post.",
        "likes": 3,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "username": "user2",
        "content": "Feeling great today! 😊",
        "likes": 5,
        "created_at": datetime.now()
    }
]

likes_tracking = {}  # For tracking user likes on posts
comments_db = {}# For tracking user comments on posts
# Sample data for doctors
doctors = [
    {
        "id": 1,
        "name": "Dr. Jane Doe",
        "specialty": "Clinical Psychologist",
        "experience": "10+ years",
        "description": "Specializes in cognitive behavioral therapy and anxiety management.",
        "image": "https://via.placeholder.com/100"
    },
    {
        "id": 2,
        "name": "Dr. John Smith",
        "specialty": "Psychiatrist",
        "experience": "15 years",
        "description": "Focuses on mood disorders and depression treatment.",
        "image": "https://via.placeholder.com/100"
    },
    {
        "id": 3,
        "name": "Dr. Sarah Lee",
        "specialty": "Family Counselor",
        "experience": "12 years",
        "description": "Expert in family counseling and child development.",
        "image": "https://via.placeholder.com/100"
    }
]

@app.route("/")
def home():
    # Render the main page; redirect to feed if the user is already logged in
    if "user" in session:
        return redirect(url_for("feed"))
    return render_template("mainpage.html")

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

        # Save user to users_db (in a real application, save to database)
        if email in users_db:
            flash("Email is already registered!", "danger")
            return render_template("signup.html")
        users_db[email] = {"username": username, "password": password}
        
        # Store user session after signup
        session["user"] = email
        flash("Signup successful! Welcome!", "success")
        return redirect(url_for("feed"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate login credentials
        user = users_db.get(email)
        if user and user["password"] == password:
            session["user"] = email  # Store session
            flash("Login successful!", "success")
            return redirect(url_for("feed"))
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
    
    return render_template("login.html")

@app.route("/feed", methods=["GET", "POST"])
def feed():
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    user = users_db.get(user_email)
    if user:
        if request.method == "POST":
            post_content = request.form.get("post_content")
            if post_content.strip():
                new_post = {
                    "id": len(posts_db) + 1,
                    "username": user["username"],
                    "content": post_content,
                    "likes": 0,
                    "created_at": datetime.now()
                }
                posts_db.insert(0, new_post)  # Add new posts at the top

        # Pass both posts and comments_db to the template
        return render_template("feed.html", username=user["username"], posts=posts_db, comments_db=comments_db)
    return redirect(url_for("login"))


@app.route("/like_post/<int:post_id>")
def like_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    post = next((p for p in posts_db if p["id"] == post_id), None)

    if post:
        # Initialize the set for this post if it doesn't exist
        if post_id not in likes_tracking:
            likes_tracking[post_id] = set()

        # Check if the user has already liked the post
        if user_email in likes_tracking[post_id]:
            flash("You can only like a post once.", "warning")
        else:
            # Add the user's email to the set and increment the like count
            likes_tracking[post_id].add(user_email)
            post["likes"] += 1
            flash("Post liked!", "success")

    return redirect(url_for("feed"))

@app.route("/comment_post/<int:post_id>", methods=["POST"])
def comment_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    comment_content = request.form.get("comment_content")
    user_email = session["user"]
    user = users_db.get(user_email)
    if user and comment_content.strip():
        comment = {
            "username": user["username"],
            "content": comment_content,
            "created_at": datetime.now()
        }
        if post_id not in comments_db:
            comments_db[post_id] = []
        comments_db[post_id].append(comment)
        flash("Comment added!", "success")
    
    return redirect(url_for("feed"))

@app.route("/profile")
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session["user"]
    user = users_db.get(user_email)
    if user:
        return render_template("profile.html", username=user["username"])
    return redirect(url_for("login"))

@app.route("/consultation", methods=["GET"])
def consultation():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Show a list of doctors with links to their booking pages
    return render_template("consultation.html", doctors=doctors)

@app.route("/booking/<int:doctor_id>")
def booking(doctor_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Fetch the selected doctor's details
    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("consultation"))
    
    return render_template("booking.html", doctor=doctor)

@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove the user from session
    flash("You have been logged out.", "info")
    return redirect(url_for("mainpage"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
