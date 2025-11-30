from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CreateAlarmResponse(BaseModel):
    id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "692b566e0ef3a85601b288f2"
            }
        }
    )


class AlarmHistoryResponse(BaseModel):
    id: str
    user_id: str
    alarm_id: str
    value: float
    triggered_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "692b566e0ef3a85601b288f2",
                "user_id": "692b566e0ef3a85601b288f2",
                "alarm_id": "692b566e0ef3a85601b288f2",
                "value": 150.0,
                "triggered_at": "2025-11-30T12:00:00"
            }
        }
    )