"""Redis client for session token storage."""

import logging
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level Redis client (initialized in lifespan)
redis_client: Optional[Redis] = None


async def init_redis() -> Redis:
    """Initialize Redis connection pool."""
    global redis_client
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    # Test connection
    try:
        await redis_client.ping()
        logger.info(f"Redis connected: {settings.REDIS_URL.split('@')[-1]}")
    except RedisError as e:
        logger.error(f"Redis connection failed: {e}")
        raise
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
        redis_client = None


def get_redis() -> Redis:
    """Get Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client


# ── Session Token Operations ──

SESSION_KEY_PREFIX = "session:"


def _session_key(token: str) -> str:
    """Generate Redis key for session token."""
    return f"{SESSION_KEY_PREFIX}{token}"


async def set_session_token(token: str, ttl_seconds: int) -> bool:
    """
    Store session token in Redis with TTL.

    Args:
        token: The session token UUID
        ttl_seconds: Time-to-live in seconds

    Returns:
        True if successful, False otherwise
    """
    try:
        redis = get_redis()
        key = _session_key(token)
        # SETEX: Set key with expiration (atomic operation)
        await redis.setex(key, ttl_seconds, "1")
        logger.debug(f"Session token stored: {token[:8]}... (TTL: {ttl_seconds}s)")
        return True
    except RedisError as e:
        logger.error(f"Failed to store session token: {e}")
        return False


async def consume_session_token(token: str) -> bool:
    """
    Atomically check and delete session token.

    This prevents replay attacks by ensuring the token can only be used once.
    Uses Redis Lua script for true atomicity (GET + DEL in single operation).

    Args:
        token: The session token UUID

    Returns:
        True if token existed and was deleted, False if not found
    """
    # Lua script: atomically get value and delete key
    # Returns 1 if key existed and was deleted, 0 if key didn't exist
    LUA_CONSUME_TOKEN = """
    local value = redis.call('GET', KEYS[1])
    if value then
        redis.call('DEL', KEYS[1])
        return 1
    else
        return 0
    end
    """
    try:
        redis = get_redis()
        key = _session_key(token)
        # Execute Lua script atomically
        result = await redis.eval(LUA_CONSUME_TOKEN, 1, key)
        if result == 1:
            logger.debug(f"Session token consumed: {token[:8]}...")
            return True
        else:
            logger.debug(f"Session token not found: {token[:8]}...")
            return False
    except RedisError as e:
        logger.error(f"Failed to consume session token: {e}")
        return False


async def check_session_token(token: str) -> bool:
    """
    Check if session token exists without consuming it.

    Args:
        token: The session token UUID

    Returns:
        True if token exists, False otherwise
    """
    try:
        redis = get_redis()
        key = _session_key(token)
        result = await redis.exists(key)
        return result > 0
    except RedisError as e:
        logger.error(f"Failed to check session token: {e}")
        return False


# ── Fingerprint Duplicate Cache Operations ──

FINGERPRINT_KEY_PREFIX = "fp:"

# Default TTL for fingerprint cache (7 days)
FINGERPRINT_CACHE_TTL = 7 * 24 * 60 * 60  # 7 days in seconds


def _fingerprint_key(fingerprint_hash: str) -> str:
    """Generate Redis key for fingerprint hash."""
    return f"{FINGERPRINT_KEY_PREFIX}{fingerprint_hash}"


async def check_fingerprint_cached(fingerprint_hash: str) -> bool:
    """
    Check if fingerprint hash exists in cache.

    Args:
        fingerprint_hash: The SHA-256 hash of the fingerprint

    Returns:
        True if fingerprint exists in cache, False otherwise
    """
    try:
        redis = get_redis()
        key = _fingerprint_key(fingerprint_hash)
        result = await redis.exists(key)
        return result > 0
    except RedisError as e:
        logger.error(f"Failed to check fingerprint cache: {e}")
        return False


async def cache_fingerprint(
    fingerprint_hash: str, ttl: int = FINGERPRINT_CACHE_TTL
) -> bool:
    """
    Cache a fingerprint hash with TTL.

    Args:
        fingerprint_hash: The SHA-256 hash of the fingerprint
        ttl: Time-to-live in seconds (default: 7 days)

    Returns:
        True if successful, False otherwise
    """
    try:
        redis = get_redis()
        key = _fingerprint_key(fingerprint_hash)
        await redis.setex(key, ttl, "1")
        logger.debug(f"Fingerprint cached: {fingerprint_hash[:16]}... (TTL: {ttl}s)")
        return True
    except RedisError as e:
        logger.error(f"Failed to cache fingerprint: {e}")
        return False
