from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime 
import secrets
from authlib.integrations.flask_client import OAuth


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

users_db = {
    "user1@example.com": {"username": "user1", "password": "password123"},
    "user2@example.com": {"username": "user2", "password": "password456"}
}

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

likes_tracking = {}
comments_db = {}
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

        if email in users_db:
            flash("Email is already registered!", "danger")
            return render_template("signup.html")
        users_db[email] = {"username": username, "password": password}
        
        session["user"] = email
        flash("Signup successful! Welcome!", "success")
        return redirect(url_for("feed"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_db.get(email)
        if user and user["password"] == password:
            session["user"] = email  
            flash("Login successful!", "success")
            return redirect(url_for("feed"))
        else:
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
    
    return render_template("login.html")

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

@app.route("/feed", methods=["GET", "POST"])
def feed():
    user_email = session.get("user")  
    if not user_email:
        return redirect(url_for("login"))  

    user = users_db.get(user_email)  

    if user:
        if request.method == "POST":
            post_content = request.form.get("post_content")
            if post_content and post_content.strip():
                new_post = {
                    "id": len(posts_db) + 1,
                    "username": user["username"],
                    "content": post_content.strip(),
                    "likes": 0,
                    "created_at": datetime.now()
                }
                posts_db.insert(0, new_post)  

        return render_template(
            "feed.html", 
            username=user["username"], 
            posts=posts_db, 
            comments_db=comments_db
        )
    return redirect(url_for("login"))

@app.route("/services")
def services():
    return render_template("service.html")  

@app.route("/resources")
def resources():
    return render_template("resources.html")




@app.route("/like_post/<int:post_id>")
def like_post(post_id):
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    post = next((p for p in posts_db if p["id"] == post_id), None)

    if post:
        if post_id not in likes_tracking:
            likes_tracking[post_id] = set()

        if user_email in likes_tracking[post_id]:
            flash("You can only like a post once.", "warning")
        else:
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

    return render_template("consultation.html", doctors=doctors)

@app.route("/booking/<int:doctor_id>")
def booking(doctor_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    doctor = next((doc for doc in doctors if doc["id"] == doctor_id), None)
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("consultation"))
    
    return render_template("booking.html", doctor=doctor)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("mainpage"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
