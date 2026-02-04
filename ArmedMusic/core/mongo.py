from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from config import MONGO_DB_URI, MONGO_DB_NAME
from ..logging import LOGGER
LOGGER(__name__).info('Connecting to your Mongo Database...')
try:
    # Quick synchronous check to fail fast on authentication or network issues
    sync_client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
    try:
        # Ping and a simple authenticated list to ensure credentials are valid
        sync_client.admin.command('ping')  # may raise OperationFailure on bad creds
        # listing database names forces auth verification in some deployments
        _ = sync_client.list_database_names()
    except OperationFailure as auth_err:
        LOGGER(__name__).error('MongoDB authentication failed. Please check your MONGO_DB_URI and credentials.\nError: %s', auth_err)
        exit(1)

    # Create async client (motor will attempt connection lazily)
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
    # Use configured database name instead of a hardcoded attribute
    mongodb = _mongo_async_[MONGO_DB_NAME]
    LOGGER(__name__).info('MongoDB client created and authenticated successfully.')
except IndexError as ie:
    # This can happen with older pymongo versions in multithreaded pools.
    LOGGER(__name__).error('MongoDB connection pool IndexError: %s. Consider upgrading pymongo and motor to recent versions.', ie)
    exit(1)
except Exception as e:
    LOGGER(__name__).error(f'Failed to initialize MongoDB client: {e}')
    exit(1)
