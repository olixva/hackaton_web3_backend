from datetime import datetime
from app.models.base_model import Model
from beanie import PydanticObjectId


class AlarmHistory(Model):
    user_id: PydanticObjectId
    alarm_id: PydanticObjectId
    value: float
    triggered_at: datetime

    class Settings:
        name = "alarm_histories"
