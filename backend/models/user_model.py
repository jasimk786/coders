from utils.db import users
from bson.objectid import ObjectId

def create_user(name, email, password_hash):
    doc = { 'name': name, 'email': email, 'password': password_hash, 'themePreference': 'dark' }
    res = users.insert_one(doc)
    return users.find_one({'_id': res.inserted_id})

def find_by_email(email):
    return users.find_one({'email': email})

def find_by_id(user_id):
    return users.find_one({'_id': ObjectId(user_id)})

def update_user(user_id, update):
    users.update_one({'_id': ObjectId(user_id)}, {'$set': update})
    return find_by_id(user_id)
