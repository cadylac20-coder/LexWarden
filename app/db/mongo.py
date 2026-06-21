import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    def connect(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGO_URI)
            cls.db = cls.client[settings.MONGO_DB_NAME]
            logger.info(f"Connected to MongoDB database: {settings.MONGO_DB_NAME}")
        except Exception as e:
            logger.error(f"Critical failure initializing MongoDB connection: {e}")
            raise e

    @classmethod
    def disconnect(cls):
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed.")
