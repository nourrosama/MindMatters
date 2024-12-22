from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# In-memory storage for feedback (replace with a database in production)
feedback_data = []

@app.route('/')
def home():
    return render_template('feedback.html')

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    feedback = request.json
    if "professional" in feedback and "rating" in feedback and "comments" in feedback:
        feedback_data.append(feedback)
        return jsonify({"message": "Feedback submitted successfully!"}), 201
    else:
        return jsonify({"error": "Invalid feedback format"}), 400

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    return jsonify(feedback_data)

if __name__ == '__main__':
    app.run(debug=True)
