import pymongo
from config import env

client = pymongo.MongoClient(f"mongodb+srv://{env.mongo_user}:{env.mongo_password}@{env.mongo_url}")
database = client["botly"]
absences = database['absence_requests']
