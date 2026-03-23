from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any
import logging
import sys

from app.config import settings
from app.schemas import MAX_PAYLOAD_BYTES, MAX_NESTING_DEPTH

logger = logging.getLogger(__name__)

MAX_QUERY_DEPTH = 5
MAX_QUERY_KEYS = 20


class QueryValidationError(Exception):
    pass


class DocumentSizeError(Exception):
    pass


class DangerousOperatorError(Exception):
    pass


def _get_object_size(obj: Any) -> int:
    if isinstance(obj, dict):
        return sys.getsizeof(obj) + sum(_get_object_size(v) for v in obj.values())
    elif isinstance(obj, list):
        return sys.getsizeof(obj) + sum(_get_object_size(item) for item in obj)
    elif isinstance(obj, str):
        return len(obj)
    else:
        return sys.getsizeof(obj)


def _validate_query_depth(query: Any, current_depth: int = 0) -> int:
    if current_depth > MAX_QUERY_DEPTH:
        raise QueryValidationError(f"Query depth exceeds maximum of {MAX_QUERY_DEPTH}")

    if isinstance(query, dict):
        if not query:
            return current_depth
        return max(_validate_query_depth(v, current_depth + 1) for v in query.values())
    elif isinstance(query, list):
        if not query:
            return current_depth
        return max(_validate_query_depth(item, current_depth + 1) for item in query)
    return current_depth


def _count_query_keys(query: Any, count: int = 0) -> int:
    if isinstance(query, dict):
        count += len(query)
        for v in query.values():
            count = _count_query_keys(v, count)
    elif isinstance(query, list):
        for item in query:
            count = _count_query_keys(item, count)
    return count


def _validate_query_structure(query: Any) -> None:
    """Validate that query contains no MongoDB operators.

    For maximum security, we only allow plain field queries.
    Any key starting with '$' is rejected as a potential security risk.
    """
    if not isinstance(query, dict):
        return

    def check_no_operators(obj: Any, path: str = "root") -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(key, str) and key.startswith("$"):
                    logger.warning(
                        f"Blocked MongoDB operator in query at {path}: {key}"
                    )
                    raise DangerousOperatorError(
                        f"MongoDB operators are not allowed. Found: {key}"
                    )
                check_no_operators(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_no_operators(item, f"{path}[{i}]")

    check_no_operators(query)

    _validate_query_depth(query)

    key_count = _count_query_keys(query)
    if key_count > MAX_QUERY_KEYS:
        raise QueryValidationError(
            f"Query has {key_count} keys, maximum allowed is {MAX_QUERY_KEYS}"
        )


def _validate_document_size(document: Any) -> None:
    size = _get_object_size(document)
    if size > MAX_PAYLOAD_BYTES:
        raise DocumentSizeError(
            f"Document size {size} bytes exceeds maximum {MAX_PAYLOAD_BYTES} bytes"
        )


class SanitizedCollection:
    """Wrapper around MongoDB collection that sanitizes all data before insertion."""

    def __init__(self, collection):
        self._collection = collection

    def _sanitize_for_mongodb(self, obj: Any) -> Any:
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

    def _sanitize_query(self, query: dict) -> dict:
        return self._sanitize_for_mongodb(query)

    def _validate_and_sanitize_query(self, query: dict) -> dict:
        _validate_query_structure(query)
        return self._sanitize_query(query)

    async def insert_one(self, document: dict) -> Any:
        _validate_document_size(document)
        sanitized = self._sanitize_for_mongodb(document)
        logger.debug("insert_one: document sanitized and validated")
        return await self._collection.insert_one(sanitized)

    async def insert_many(self, documents: list[dict]) -> Any:
        for doc in documents:
            _validate_document_size(doc)
        sanitized_documents = [self._sanitize_for_mongodb(doc) for doc in documents]
        logger.debug(f"insert_many: {len(documents)} documents sanitized and validated")
        return await self._collection.insert_many(sanitized_documents)

    async def find_one(self, filter: dict | None = None, *args, **kwargs) -> Any:
        if filter:
            filter = self._validate_and_sanitize_query(filter)
        return await self._collection.find_one(filter, *args, **kwargs)

    async def find(self, filter: dict | None = None, *args, **kwargs) -> Any:
        if filter:
            filter = self._validate_and_sanitize_query(filter)
        return self._collection.find(filter, *args, **kwargs)

    async def update_one(self, filter: dict, update: dict, *args, **kwargs) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        update = self._validate_and_sanitize_query(update)
        logger.debug("update_one: filter and update validated and sanitized")
        return await self._collection.update_one(filter, update, *args, **kwargs)

    async def update_many(self, filter: dict, update: dict, *args, **kwargs) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        update = self._validate_and_sanitize_query(update)
        logger.debug("update_many: filter and update validated and sanitized")
        return await self._collection.update_many(filter, update, *args, **kwargs)

    async def delete_one(self, filter: dict, *args, **kwargs) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        logger.debug("delete_one: filter validated and sanitized")
        return await self._collection.delete_one(filter, *args, **kwargs)

    async def delete_many(self, filter: dict, *args, **kwargs) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        logger.debug("delete_many: filter validated and sanitized")
        return await self._collection.delete_many(filter, *args, **kwargs)

    async def aggregate(self, pipeline: list, *args, **kwargs) -> Any:
        if pipeline:
            validated_pipeline = []
            for stage in pipeline:
                validated_stage = self._validate_and_sanitize_query(stage)
                validated_pipeline.append(validated_stage)
            logger.debug(f"aggregate: {len(pipeline)} pipeline stages validated")
            return self._collection.aggregate(validated_pipeline, *args, **kwargs)
        return self._collection.aggregate(pipeline, *args, **kwargs)

    async def find_one_and_delete(self, filter: dict, *args, **kwargs) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        logger.debug("find_one_and_delete: filter validated and sanitized")
        return await self._collection.find_one_and_delete(filter, *args, **kwargs)

    async def find_one_and_update(
        self, filter: dict, update: dict, *args, **kwargs
    ) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        update = self._validate_and_sanitize_query(update)
        logger.debug("find_one_and_update: filter and update validated and sanitized")
        return await self._collection.find_one_and_update(
            filter, update, *args, **kwargs
        )

    async def find_one_and_replace(
        self, filter: dict, replacement: dict, *args, **kwargs
    ) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        _validate_document_size(replacement)
        replacement = self._sanitize_for_mongodb(replacement)
        logger.debug(
            "find_one_and_replace: filter and replacement validated and sanitized"
        )
        return await self._collection.find_one_and_replace(
            filter, replacement, *args, **kwargs
        )

    async def replace_one(
        self, filter: dict, replacement: dict, *args, **kwargs
    ) -> Any:
        filter = self._validate_and_sanitize_query(filter)
        _validate_document_size(replacement)
        replacement = self._sanitize_for_mongodb(replacement)
        logger.debug("replace_one: filter and replacement validated and sanitized")
        return await self._collection.replace_one(filter, replacement, *args, **kwargs)

    async def count_documents(self, filter: dict, *args, **kwargs) -> int:
        filter = self._validate_and_sanitize_query(filter)
        return await self._collection.count_documents(filter, *args, **kwargs)


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
