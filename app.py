from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("mainpage.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password != confirm_password:
            return "Passwords do not match!", 400
        
        # Add logic to save user details to the database
        return redirect(url_for("home"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Validate login credentials
        return redirect(url_for("home"))
    
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
