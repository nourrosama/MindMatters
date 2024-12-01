from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For session management

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

@app.route("/feed")
def feed():
    # Check if user is logged in, otherwise redirect to login
    if "user" not in session:
        return redirect(url_for("login"))

    user_email = session["user"]
    user = users_db.get(user_email)
    if user:
        return render_template("feed.html", username=user["username"])
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove the user from session
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
