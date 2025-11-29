from fastapi import APIRouter

# DTOs
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_request import GenerateChartMeterRequest
from app.dtos.meter.meter_response import CreateMeterResponse
# Services
from app.services.meter_service import MeterService

meter_router = APIRouter(prefix="/meter", tags=["meter"])


@meter_router.post("", response_model=CreateMeterResponse)
async def create_meter(request: CreateMeterRequest):
    return await MeterService.create_meter(request)

@meter_router.post("/chart", response_model=GenerateChartMeterResponse)
async def generate_chart(request: GenerateChartMeterRequest):
    return await MeterService.generate_chart(request)