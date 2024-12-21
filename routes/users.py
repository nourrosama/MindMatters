from flask import Blueprint, jsonify
from bson.json_util import dumps
from app_2 import users_collection  # Import your collection

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
def get_users():
    users = list(users_collection.find())  # Fetch all users
    return dumps(users), 200  # Convert BSON to JSON
