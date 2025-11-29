from enum import Enum
from app.models.base_model import Model
from datetime import datetime
from pydantic import Field
from beanie import PydanticObjectId


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class Payment(Model):
    user_id: PydanticObjectId
    meter_reading_id: PydanticObjectId
    amount_sats: float
    amount_euro: float
    tx_id: str
    status: PaymentStatus = Field(PaymentStatus.PENDING)
    created_at: datetime
    confirmed_at: datetime | None = None
    
    class Settings:
        name = "payments"