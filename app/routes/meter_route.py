from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

# DTOs
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_request import StepEnum
from app.dtos.meter.meter_response import CreateMeterResponse
# Models
from app.models.user import User
# Services
from app.services.meter_service import MeterService
# Utils
from app.utils.whatsonchain_utils import WhatsOnChainUtils
# x402
# Removed imports to avoid validation issues with BSV
import json
from x402.encoding import safe_base64_decode

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

@meter_router.get("/chart/users")
async def get_users_chart(request: Request):
    # Manual x402 payment check for BSV
    payment_requirements = {
        "scheme": "exact",
        "network": "bsv",  # Custom for BSV
        "asset": "BSV",
        "maxAmountRequired": "100 satoshis",
        "resource": str(request.url),
        "description": "",
        "mimeType": "",
        "payTo": "12HKnZrJ8Fcx2F8SgJHUrV9uvGNo4eoveD",
        "maxTimeoutSeconds": 60,
    }
    
    payment_header = request.headers.get("X-PAYMENT", "")
    if payment_header == "":
        return JSONResponse(
            content={
                "x402Version": 1,
                "accepts": [payment_requirements],
                "error": "X-PAYMENT header not provided"
            },
            status_code=402
        )
    
    # Decode payment header (assuming it's base64 encoded JSON with txid)
    try:
        payment_data = json.loads(safe_base64_decode(payment_header))
        txid = payment_data.get("txid")
        if not txid:
            raise ValueError("No txid in payment data")
    except Exception as e:
        return JSONResponse(
            content={
                "x402Version": 1,
                "accepts": [payment_requirements],
                "error": "Invalid payment header format"
            },
            status_code=402
        )
    
    # Validate transaction
    if not await WhatsOnChainUtils.validate_transaction(txid, "12HKnZrJ8Fcx2F8SgJHUrV9uvGNo4eoveD", 100):
        return JSONResponse(
            content={
                "x402Version": 1,
                "accepts": [payment_requirements],
                "error": "Invalid or unconfirmed transaction"
            },
            status_code=402
        )
    
    # Aggregate data for all users
    users = await User.find_all().to_list()
    
    total_users = len(users)
    total_balance_euro = 0.0
    total_monthly_kwh = 0.0
    
    for user in users:
        if user.user_wallet and user.user_wallet.bsv_address:
            balance_satoshis = await WhatsOnChainUtils.get_balance(user.user_wallet.bsv_address)
            balance_euro = await WhatsOnChainUtils.convert_satoshis_to_euro(balance_satoshis)
            total_balance_euro += balance_euro
        
        monthly_kwh = await MeterService.get_monthly_usage_kwh(str(user.id))
        total_monthly_kwh += monthly_kwh
    
    return {
        "total_users": total_users,
        "total_balance_euro": total_balance_euro,
        "total_monthly_kwh": total_monthly_kwh,
    }