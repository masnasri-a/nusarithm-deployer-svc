from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database():
    mongo_uri = os.getenv("MONGO_URI")
    logger.info(f"Connecting to MongoDB {mongo_uri}...")
    db_name = os.getenv("DB_NAME", "deployerapp")
    client = MongoClient(mongo_uri)
    return client[db_name]