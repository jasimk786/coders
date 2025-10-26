from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_fake_news')

client = MongoClient(MONGO_URI)
db = client.get_default_database() if client else None

# Ensure collections
users = db.get_collection('users')
history = db.get_collection('history')
