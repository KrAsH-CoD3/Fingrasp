from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SanitizedCollection:
    """Wrapper around MongoDB collection that sanitizes all data before insertion."""

    def __init__(self, collection):
        self._collection = collection

    async def insert_one(self, document: dict) -> Any:
        """Insert a single document after sanitizing."""
        sanitized = self._sanitize_for_mongodb(document)
        return await self._collection.insert_one(sanitized)

    async def find_one(self, *args, **kwargs):
        return await self._collection.find_one(*args, **kwargs)

    async def find(self, *args, **kwargs):
        return self._collection.find(*args, **kwargs)

    async def insert_many(self, documents: list[dict]) -> Any:
        """Insert multiple documents after sanitizing."""
        sanitized_documents = [self._sanitize_for_mongodb(doc) for doc in documents]
        return await self._collection.insert_many(sanitized_documents)
    
    def _sanitize_for_mongodb(self, obj: Any) -> Any:
        """
        Recursively sanitize data to prevent NoSQL injection.
        Removes keys that start with '$' or contain '.' (MongoDB operators).
        This is a defense-in-depth measure in addition to Pydantic validation.
        """
        if isinstance(obj, dict):
            sanitized = {}
            for key, value in obj.items():
                if isinstance(key, str):
                    if key.startswith("$") or "." in key:
                        logger.warning(
                            f"Removed potentially malicious key from data: {key[:20]}"
                        )
                        continue
                    sanitized[key] = self._sanitize_for_mongodb(value)
                else:
                    sanitized[key] = self._sanitize_for_mongodb(value)
            return sanitized
        elif isinstance(obj, list):
            return [self._sanitize_for_mongodb(item) for item in obj]
        else:
            return obj


class SanitizedDatabase:
    """Wrapper around MongoDB database that returns sanitized collections."""

    def __init__(self, database):
        self._db = database
        self._collections = {}

    def __getitem__(self, name: str):
        if name not in self._collections:
            self._collections[name] = SanitizedCollection(self._db[name])
        return self._collections[name]



def setup_db() -> tuple[AsyncIOMotorClient, SanitizedDatabase]:
    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=10_000,
        socketTimeoutMS=30_000,
        maxPoolSize=10,
        minPoolSize=1,
    )
    
    # Wrap the database for sanitization
    sanitized_db = SanitizedDatabase(client[settings.DB_NAME])
    return client, sanitized_db

