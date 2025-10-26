from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models.user_model import create_user, find_by_email, find_by_id, update_user
import bcrypt
from utils.jwt_helper import generate_token, verify_token
from functools import wraps
from models.history_model import create_history, get_history_for_user
import torch.nn.functional as F
import numpy as np

load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174'])

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

# Load model once (lazy loading)
MODEL_NAME = 'bert-base-uncased'
LOCAL_MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'fine_tuned_bert')

def load_model_and_tokenizer():
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        if os.path.exists(os.path.join(LOCAL_MODEL_DIR, 'config.json')):
            tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIR)
            model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_DIR)
        else:
            tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
        return tokenizer, model
    except Exception as e:
        raise Exception(f"Failed to load model: {str(e)}")

tokenizer = None
model = None

def get_model_and_tokenizer():
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer, model = load_model_and_tokenizer()
        if not hasattr(model.config, 'id2label'):
            model.config.id2label = {0: 'Fake', 1: 'Real'}
            model.config.label2id = {'Fake': 0, 'Real': 1}
        model.eval()
    return tokenizer, model


@app.route('/')
def home():
    return jsonify({'message':'AI Fake News Detector API'})

@app.route('/signup', methods=['POST'])
def signup():
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

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    if not (email and password):
        return jsonify({'message':'Missing fields'}), 400
    user = find_by_email(email)
    if not user:
        return jsonify({'message':'Invalid credentials'}), 401
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message':'Invalid credentials'}), 401
    token = generate_token(user['_id'])
    return jsonify({'token': token, 'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email']}})

@app.route('/analyzeText', methods=['POST'])
@token_required
def analyze_text():
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({'message':'No text provided'}), 400

        tokenizer, model = get_model_and_tokenizer()
        import torch
        inputs = tokenizer(text, truncation=True, padding=True, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1).squeeze().tolist()

        pred_index = np.argmax(probs)
        prediction = model.config.id2label[pred_index]
        confidence = probs[pred_index] * 100.0

        hist = create_history(request.user, text, prediction, confidence)
        return jsonify({'prediction': prediction, 'confidence': confidence, 'text': text, 'historyId': str(hist['_id'])})
    except Exception as e:
        return jsonify({'message': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyzeImage', methods=['POST'])
@token_required
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'message':'No image uploaded'}), 400
    img = request.files['image']
    from PIL import Image
    import pytesseract

    image = Image.open(img.stream)
    extracted = pytesseract.image_to_string(image)
    if not extracted.strip():
        return jsonify({'message':'No text found in image', 'text': ''}), 200

    tokenizer, model = get_model_and_tokenizer()
    import torch
    inputs = tokenizer(extracted, truncation=True, padding=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1).squeeze().tolist()

    pred_index = np.argmax(probs)
    prediction = model.config.id2label[pred_index]
    confidence = probs[pred_index] * 100.0

    hist = create_history(request.user, extracted, prediction, confidence, image_url=None)
    return jsonify({'prediction': prediction, 'confidence': confidence, 'text': extracted, 'historyId': str(hist['_id'])})

@app.route('/profile', methods=['GET'])
@token_required
def get_profile():
    user = find_by_id(request.user)
    if not user:
        return jsonify({'message':'User not found'}), 404
    return jsonify({'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'themePreference': user.get('themePreference', 'dark')}})

@app.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    data = request.json
    update_data = {}
    if 'name' in data:
        update_data['name'] = data['name']
    if 'email' in data:
        update_data['email'] = data['email']
    user = update_user(request.user, update_data)
    return jsonify({'user': {'id': str(user['_id']), 'name': user['name'], 'email': user['email'], 'themePreference': user.get('themePreference', 'dark')}})

@app.route('/history', methods=['GET'])
@token_required
def get_history():
    history = get_history_for_user(request.user)
    return jsonify({'history': [{'id': str(h['_id']), 'text': h['inputText'], 'prediction': h['prediction'], 'confidence': h['confidence'], 'timestamp': h['createdAt'], 'image_url': h.get('imageUrl')} for h in history]})

@app.route('/settings', methods=['PUT'])
@token_required
def update_settings():
    data = request.json
    if 'theme' in data:
        update_user(request.user, {'themePreference': data['theme']})
    return jsonify({'message':'Settings updated'})


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
