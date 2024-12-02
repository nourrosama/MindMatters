from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For session management

# In-memory database for users (use a real database in production)
users_db = {
    "user1@example.com": {"username": "user1", "password": "password123"},
    "user2@example.com": {"username": "user2", "password": "password456"}
}

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
