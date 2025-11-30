from app.models.base_model import Model
from beanie import PydanticObjectId
from datetime import datetime


class MeterReading(Model):
    """Meter reading document model for energy consumption data."""
    payment_id: PydanticObjectId | None = None
    user_id: PydanticObjectId
    kw_consumed: float
    cost_euro: float | None = None
    meter_id: str
    timestamp: datetime

    class Settings:
        name = "meter_readings"
