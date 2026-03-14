from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]


def connect_db():
    """Return the database instance (useful for dependency injection later)."""

    return db
