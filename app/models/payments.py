from beanie import Document
from datetime import datetime
from bson import ObjectId


class Payment(Document):
    user_id: ObjectId
    amount: float
    currency: str
    status: str
    created_at: datetime
    
    class Settings:
        name = "payments"
