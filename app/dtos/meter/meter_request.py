from pydantic import BaseModel, ConfigDict
from enum import Enum

# Request model for creating a new meter reading entry
class CreateMeterRequest(BaseModel):
    user_id: str
    meter_id: str
    reading: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "692b2e7deed34135d7cf5a8c",
                "meter_id": "meter_12345",
                "reading": 1500.75
            }
        }
    )

# Enumeration for chart aggregation steps (daily, weekly, etc.)
class StepEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"
