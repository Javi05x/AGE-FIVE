import os
from functools import lru_cache
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGO_DB", "ProyectoFutbol")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "Jugadores")


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_collection():
    client = get_client()
    db = client[MONGO_DB]
    return db[MONGO_COLLECTION]
