from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from config import MONGO_DB_URI, MONGO_DB_NAME
from ..logging import LOGGER
LOGGER(__name__).info('Connecting to your Mongo Database...')
try:
    # Quick synchronous check to fail fast on authentication or network issues
    sync_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
    sync_client.admin.command('ping')  # will raise on auth issues

    # Create async client (motor will attempt connection lazily)
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
    # Use configured database name instead of a hardcoded attribute
    mongodb = _mongo_async_[MONGO_DB_NAME]
    LOGGER(__name__).info('MongoDB client created and authenticated successfully.')
except Exception as e:
    LOGGER(__name__).error(f'Failed to initialize MongoDB client: {e}')
    exit(1)
