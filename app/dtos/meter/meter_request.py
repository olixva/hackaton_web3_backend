from pydantic import BaseModel, ConfigDict
from enum import Enum

## Create Meter Request ##

class CreateMeterRequest(BaseModel):
    payment_id: str | None = None
    user_id: str
    cost_euro: float | None = None
    meter_id: str
    reading: float

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "payment_id": "692b2e7deed34135d7cf5a8c",
                "user_id": "692b2e7deed34135d7cf5a8c",
                "cost_euro": 12.5,
                "meter_id": "meter_12345",
                "reading": 1500.75
            }
        }
    )

## Generate Chart Request ##

class StepEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    HOURLY = "hourly"


class GenerateChartMeterRequest(BaseModel):
    user_id: str
    start_date: str | None = None 
    end_date: str | None = None 
    step: StepEnum = StepEnum.MONTHLY

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "692b2e7deed34135d7cf5a8c",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "step": "monthly"
            }
        }
    )

