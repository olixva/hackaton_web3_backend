from beanie import Document
from datetime import datetime
from bson import ObjectId


class MeterReading(Document):
    user_id: ObjectId
    meter_id: str
    reading: float
    timestamp: datetime

    class Settings:
        name = "meter_readings"
