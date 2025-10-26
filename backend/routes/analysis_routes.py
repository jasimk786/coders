from flask import Blueprint, request, jsonify
from models.history_model import create_history
from utils.jwt_helper import verify_token
from functools import wraps
import os

bp = Blueprint('analysis', __name__)

# Load model once
# from transformers import AutoTokenizer, AutoModelForSequenceClassification  # Moved inside functions
# import torch  # Moved inside functions
import torch.nn.functional as F
import numpy as np
import os

# Prefer a locally fine-tuned model directory. If present, load from disk to avoid
# downloading from the Hub. Otherwise fall back to the Hub model name below.
# Note: bert-base-uncased is a base model (~110M params); for better accuracy, fine-tune it on your data using bert_finetune.py
LOCAL_MODEL_DIR = "E:/mp/fine_tuned_bert"  # Hardcoded path to our fine-tuned model

# Resolve real local path (normalize)
LOCAL_MODEL_DIR = os.path.normpath(LOCAL_MODEL_DIR)

def load_model_and_tokenizer():
    try:
        # Import here to avoid Flask import conflicts
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        # Always load from our fine-tuned model directory
        if os.path.exists(os.path.join(LOCAL_MODEL_DIR, 'config.json')):
            print(f'Loading fine-tuned model from: {LOCAL_MODEL_DIR}')
            tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_DIR)
            model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_DIR)
            return tokenizer, model
        else:
            raise Exception(f"Fine-tuned model not found at {LOCAL_MODEL_DIR}")

    except Exception as e:
        print(f"Critical error loading fine-tuned model: {str(e)}")
        raise Exception(f"Failed to load fine-tuned model: {str(e)}")


# Global variables for lazy loading
tokenizer = None
model = None

def get_model_and_tokenizer():
    global tokenizer, model
    if tokenizer is None or model is None:
        tokenizer, model = load_model_and_tokenizer()
        # Ensure label mapping is set (for base models without fine-tuning)
        if not hasattr(model.config, 'id2label') or len(model.config.id2label) != 2:
            model.config.id2label = {0: 'Fake', 1: 'Real'}
            model.config.label2id = {'Fake': 0, 'Real': 1}
        model.eval()
    return tokenizer, model

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print("DEBUG: token_required called")
        auth = request.headers.get('Authorization', None)
        if not auth:
            print("DEBUG: No Authorization header")
            return jsonify({'message':'Token missing'}), 401
        parts = auth.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            print("DEBUG: Invalid token format")
            return jsonify({'message':'Invalid token format'}), 401
        token = parts[1]
        print(f"DEBUG: Verifying token: {token[:20]}...")
        payload = verify_token(token)
        if not payload:
            print("DEBUG: Token verification failed")
            return jsonify({'message':'Invalid or expired token'}), 401
        request.user = payload['sub']
        print(f"DEBUG: Token valid, user: {request.user}")
        return f(*args, **kwargs)
    return decorated


@bp.route('/analyzeText', methods=['POST'])
@token_required
def analyze_text():
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({'message':'No text provided'}), 400

        # Get model and tokenizer (lazy loading)
        tokenizer, model = get_model_and_tokenizer()

        # Import torch here to avoid Flask import conflicts
        import torch

        # Tokenize and run model
        inputs = tokenizer(text, truncation=True, padding=True, return_tensors='pt')
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1).squeeze().tolist()

        # Get prediction using label mapping
        pred_index = np.argmax(probs)
        prediction = model.config.id2label[pred_index]
        confidence = probs[pred_index] * 100.0

        # Persist to DB
        hist = create_history(request.user, text, prediction, confidence)

        return jsonify({'prediction': prediction, 'confidence': confidence, 'text': text, 'historyId': str(hist['_id'])})
    except Exception as e:
        print(f"Error in analyze_text: {str(e)}")
        return jsonify({'message': f'Analysis failed: {str(e)}'}), 500



