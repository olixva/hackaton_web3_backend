from pydantic import BaseModel, ConfigDict


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
