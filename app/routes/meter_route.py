from fastapi import APIRouter, HTTPException

# DTOs
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_request import StepEnum
from app.dtos.meter.meter_response import CreateMeterResponse
# Services
from app.services.meter_service import MeterService

meter_router = APIRouter(prefix="/meter", tags=["meter"])


@meter_router.post("", response_model=CreateMeterResponse)
async def create_meter(request: CreateMeterRequest):
    return await MeterService.create_meter(request)

@meter_router.get("/chart", response_model=GenerateChartMeterResponse)
async def generate_chart(
    user_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    step: str = "daily"
):
    try:
        step_enum = StepEnum(step)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid step value")
    
    return await MeterService.generate_chart(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        step=step_enum
    )