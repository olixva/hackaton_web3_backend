from enum import Enum
from beanie import Document
from datetime import datetime
from bson import ObjectId
from pydantic import Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class Payment(Document):
    user_id: ObjectId
    meter_reading_id: ObjectId
    amount_sats: float
    amount_euro: float
    tx_id: str
    status: PaymentStatus = Field(PaymentStatus.PENDING)
    created_at: datetime
    confirmed_at: datetime | None = None
    
    class Settings:
        name = "payments"