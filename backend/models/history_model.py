from utils.db import history
from bson.objectid import ObjectId

def create_history(user_id, input_text, prediction, confidence, image_url=None):
    doc = {
        'userId': ObjectId(user_id),
        'inputText': input_text,
        'prediction': prediction,
        'confidence': float(confidence),
        'imageUrl': image_url,
        'createdAt': __import__('datetime').datetime.utcnow()
    }
    res = history.insert_one(doc)
    return history.find_one({'_id': res.inserted_id})

def get_history_for_user(user_id):
    return list(history.find({'userId': ObjectId(user_id)}).sort('createdAt', -1))
