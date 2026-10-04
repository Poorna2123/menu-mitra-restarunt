from pymongo import MongoClient

# Local MongoDB connection string
MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)
db = client['restaurant_db']

# Collections
users_collection = db['users']
orders_collection = db['orders']
