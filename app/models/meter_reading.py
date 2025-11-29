from beanie import Document, PydanticObjectId
from datetime import datetime


class MeterReading(Document):
<<<<<<< HEAD
    user_id: ObjectId
    payment_id: ObjectId | None = None
    kw_consumed: float
    cost_euro: float | None = None
=======
    user_id: PydanticObjectId
    meter_id: str
    reading: float
>>>>>>> de72181 (feat: implement user retrieval service and response model)
    timestamp: datetime

    class Settings:
        name = "meter_readings"
