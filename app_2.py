from flask import Flask, render_template, request, redirect, url_for, session
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

# Sample data for users (in a real application, this should be stored in a database)
users_db = {
    "user1@example.com": {"username": "user1", "password": "password123"},
    "user2@example.com": {"username": "user2", "password": "password456"}
}

@app.route("/")
def home():
    # Render the main page, check if user is logged in and redirect to feed if so
    if "user" in session:
        return redirect(url_for("feed"))
    return render_template("mainpage.html")

@app.route("/messages")
def messages():
    # Render the messages page
    return render_template("messages.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            return "Passwords do not match!", 400
        
        # Save user to the users_db for the example (in a real case, save it to a database)
        if email in users_db:
            return "Email is already registered!", 400
        users_db[email] = {"username": username, "password": password}
        
        # Store user session after signup
        session["user"] = email
        
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
            return redirect(url_for("feed"))
        else:
            return render_template("login.html", error="Invalid credentials")  # Display error message
    
    return render_template("login.html")

@app.route("/login/google")
def login_google():
    return google.authorize_redirect(url_for("authorize_google", _external=True))

@app.route("/authorize/google")
def authorize_google():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    
    # Store user information in the session
    session['user'] = {
        'provider': 'Google',
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'picture': user_info.get('picture')
    }

    return redirect(url_for("feed"))  # Redirect to your feed or dashboard

@app.route("/login/facebook")
def login_facebook():
    return facebook.authorize_redirect(url_for("authorize_facebook", _external=True))

@app.route("/authorize/facebook")
def authorize_facebook():
    token = facebook.authorize_access_token()
    user_info = facebook.get('me?fields=id,name,email,picture').json()

    # Store user information in the session
    session['user'] = {
        'provider': 'Facebook',
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'picture': user_info['picture']['data']['url']
    }

    return redirect(url_for("feed"))  # Redirect to your feed or dashboard

@app.route("/feed")
def feed():
    # Check if the user is logged in
    user_email = session.get("user")  # Get the user from the session
    if not user_email:
        return redirect(url_for("login"))  # Redirect to login if not logged in

    # Retrieve user details from a database or session
    user = users_db.get(user_email)  # Assuming `users_db` contains user data
    if user:
        return render_template("feed.html", username=user["username"])  # Display feed with username
    
    # If user not found in the database, redirect to login
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove the user from session
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
