from beanie import Document
from datetime import datetime
from bson import ObjectId


class MeterReading(Document):
    user_id: ObjectId
    payment_id: ObjectId | None = None
    kw_consumed: float
    cost_euro: float | None = None
    timestamp: datetime

    class Settings:
        name = "meter_readings"
