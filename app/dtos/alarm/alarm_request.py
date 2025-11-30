from pydantic import BaseModel, ConfigDict

from app.models.alarm import AlarmType


class CreateAlarmRequest(BaseModel):
    user_id: str
    threshold: float
    type: AlarmType
    active: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "692b566e0ef3a85601b288f2",
                "threshold": 100.0,
                "type": "money",
                "active": True
            }
        }
    )