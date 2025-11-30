from pymongo import AsyncMongoClient
from beanie import init_beanie
# Import application settings
from app.config.settings import settings
# Import document models for Beanie
from app.models.alarm_history import AlarmHistory
from app.models.meter_reading import MeterReading
from app.models.payment import Payment
from app.models.user import User
from app.models.alarm import Alarm


class MongoDbClient:
    """MongoDB client wrapper for Beanie ODM initialization and connection management."""

    def __init__(self, database_name: str = "hackaton_web3_db"):
        # List of document models to register with Beanie
        self.models = [MeterReading, Payment, User, Alarm, AlarmHistory]
        # Create asynchronous MongoDB client using settings URL
        self.client = AsyncMongoClient(settings.MONGODB_URL)
        self.database_name = database_name

    async def init(self):
        """Initialize Beanie with the database and document models."""
        try:
            await init_beanie(
                database=self.client[self.database_name], document_models=self.models
            )
        except Exception as e:
            raise ValueError(f"Error initializing database: {e}")

    async def close(self):
        """Close the MongoDB client connection."""
        try:
            await self.client.close()
        except Exception as e:
            raise ValueError(f"Error closing database connection: {e}")