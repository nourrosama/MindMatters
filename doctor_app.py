# import sqlite3
from flask import Flask, render_template, jsonify, request

app = Flask(__name__, static_folder='static', template_folder='templates')

# Database setup
# def init_db():
#     conn = sqlite3.connect('mydb2.db')  
#     c = conn.cursor()  
#     c.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT NOT NULL,
#         email TEXT NOT NULL,
#         password TEXT NOT NULL
#     )
#     ''')
#     conn.commit()
#     conn.close()


# Serve the main dashboard page
@app.route('/')
def index():
    return render_template('index.html')

# # Sample data for appointments
appointments = [
    {"patient": "Khaled", "location": "New Cairo", "date": "4 Jan 2024", "time": "10:30 PM"},
    {"patient": "Adam", "location": "Giza", "date": "5 Feb 2024", "time": "9:30 PM"},
    {"patient": "Ahmed", "location": "Cairo", "date": "15 Jan 2024", "time": "1:40 PM"}
]

# API endpoint to fetch appointments
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    return jsonify(appointments)

# API endpoint to add a new appointment
@app.route('/api/appointments', methods=['POST'])
def add_appointment():
    new_appointment = request.json
    appointments.append(new_appointment)
    return jsonify({"message": "Appointment added successfully!", "appointments": appointments}), 201

# Static files (CSS)
@app.route('/styles.css')
def styles():
    return app.send_static_file('styles.css')

if __name__ == '__main__':
    app.run(debug=True)
