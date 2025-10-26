from flask import Blueprint, request, jsonify
from models.user_model import create_user, find_by_email
import bcrypt
from utils.jwt_helper import generate_token

auth_bp = Blueprint('auth_routes', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    print("DEBUG: signup route called")
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not (name and email and password):
        return jsonify({'message':'Missing fields'}), 400
    if find_by_email(email):
        return jsonify({'message':'Email already exists'}), 400
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = create_user(name, email, pw_hash)
    return jsonify({'message':'User created', 'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email']}}), 201


@auth_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message':'Auth blueprint working'})
