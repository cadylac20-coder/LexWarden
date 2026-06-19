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
            # Pull data collection context cleanly out of URI
            db_name = settings.MONGO_URI.split("/")[-1].split("?")[0]
            if not db_name:
                db_name = "lexwarden"
            cls.db = cls.client[db_name]
            logger.info(f"Connected to MongoDB database instance: {db_name}")
        except Exception as e:
            logger.error(f"Critical failure initializing MongoDB connection: {e}")
            raise e

    @classmethod
    def disconnect(cls):
        if cls.client:
            cls.client.close()
            logger.info("MongoDB structural pooling layer closed safely.")
