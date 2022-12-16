import pymongo
from config import env

client = pymongo.MongoClient(f"mongodb+srv://{env.mongo_user}:{env.mongo_password}@{env.mongo_url}")
database = client[str(env.mongo_database_name)]
users = database[str(env.mongo_users_collection_name)]
absences = database[str(env.mongo_absence_requests_collection_name)]
