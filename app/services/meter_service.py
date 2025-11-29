from datetime import datetime
from fastapi import HTTPException

# DTOs
from app.dtos.meter.meter_response import CreateMeterResponse
from app.dtos.meter.meter_request import CreateMeterRequest
# Models
from app.models.meter_reading import MeterReading
from beanie import PydanticObjectId


class MeterService:

    @staticmethod
    async def create_meter(request: CreateMeterRequest) -> CreateMeterResponse:
        if not MeterReading.is_valid_id(request.user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        if not request.payment_id:
            raise HTTPException(status_code=400, detail="Not paid yet")

        if not MeterReading.is_valid_id(request.payment_id):
            raise HTTPException(status_code=400, detail="Invalid payment ID format")

        new_meter = MeterReading(
            user_id=PydanticObjectId(request.user_id),
            kw_consumed=request.reading, # TODO: Calculate kw_consumed based on previous reading
            meter_id=request.meter_id,
            reading=request.reading,
            payment_id=PydanticObjectId(request.payment_id) if request.payment_id else None,
            timestamp=datetime.now(),
        )
        await new_meter.insert()

        return CreateMeterResponse(id=str(new_meter.id))