from app.models.base_model import Model
from datetime import datetime
from beanie import PydanticObjectId


class Payment(Model):
    """Payment document model for BSV transactions."""
    user_id: PydanticObjectId
    amount_sats: float
    amount_euro: float
    tx_id: str
    created_at: datetime

    class Settings:
        name = "payments"