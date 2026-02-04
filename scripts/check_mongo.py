"""Small utility to validate MONGO_DB_URI from environment and test authentication.
Run: python3 scripts/check_mongo.py
"""
from os import getenv
import sys
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

MONGO_DB_URI = getenv('MONGO_DB_URI')
if not MONGO_DB_URI:
    print('ERROR: MONGO_DB_URI environment variable is not set.')
    sys.exit(2)

print('Testing MongoDB connection...')
try:
    client = MongoClient(MONGO_DB_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('Ping succeeded. Authentication OK.')
    print('Databases:', client.list_database_names())
except OperationFailure as e:
    print('Authentication failed. Please verify username/password and authSource in MONGO_DB_URI.')
    print('Error:', e)
    sys.exit(3)
except ServerSelectionTimeoutError as e:
    print('Server selection/connection timed out. Check host network and that the MongoDB server is reachable.')
    print('Error:', e)
    sys.exit(4)
except Exception as e:
    print('Unexpected error while connecting to MongoDB:', e)
    sys.exit(1)
print('OK')
