from flask import Blueprint, request, jsonify
from models.user_model import find_by_id, update_user, find_by_email
from models.history_model import get_history_for_user
from utils.jwt_helper import verify_token
from functools import wraps
from bson.objectid import ObjectId

bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth:
            return jsonify({'message':'Token missing'}), 401
        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'message':'Invalid token format'}), 401
        token = parts[1]
        payload = verify_token(token)
        if not payload:
            return jsonify({'message':'Invalid or expired token'}), 401
        request.user = payload['sub']
        return f(*args, **kwargs)
    return decorated


@bp.route('/profile', methods=['GET'])
@token_required
def profile_get():
    user = find_by_id(request.user)
    if not user:
        return jsonify({'message':'User not found'}), 404
    return jsonify({'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'themePreference': user.get('themePreference', 'dark')}})


@bp.route('/profile', methods=['PUT'])
@token_required
def profile_update():
    data = request.json
    update = {}
    if 'name' in data:
        update['name'] = data['name']
    if 'password' in data and data['password']:
        import bcrypt
        update['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    user = update_user(request.user, update)
    return jsonify({'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email']}})


@bp.route('/history', methods=['GET'])
@token_required
def history():
    items = get_history_for_user(request.user)
    # Convert ObjectIds and datetimes
    def serialize(h):
        return {
            '_id': str(h['_id']),
            'prediction': h.get('prediction'),
            'confidence': h.get('confidence'),
            'text': h.get('inputText'),
            'imageUrl': h.get('imageUrl'),
            'createdAt': h.get('createdAt').isoformat() if h.get('createdAt') else None
        }
    return jsonify({'history': [serialize(h) for h in items]})


@bp.route('/settings', methods=['PUT'])
@token_required
def settings_update():
    data = request.json
    theme = data.get('theme')
    if theme not in ('light', 'dark'):
        return jsonify({'message':'Invalid theme'}), 400
    user = update_user(request.user, {'themePreference': theme})
    return jsonify({'message':'Settings updated', 'theme': theme})
