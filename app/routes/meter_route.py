from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

# Import DTOs for meter request and response models
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_request import StepEnum
from app.dtos.meter.meter_response import CreateMeterResponse
# Import User model for aggregation
from app.models.user import User
# Import meter service for business logic
from app.services.meter_service import MeterService
# Import utilities for BSV operations
from app.utils.whatsonchain_utils import WhatsOnChainUtils
# Import for manual x402 payment decoding
import json
from x402.encoding import safe_base64_decode

# Create router for meter-related endpoints with prefix and tags
meter_router = APIRouter(prefix="/meter", tags=["meter"])

# Endpoint to create a new meter reading
@meter_router.post("", response_model=CreateMeterResponse)
async def create_meter(request: CreateMeterRequest):
    return await MeterService.create_meter(request)

# Endpoint to generate consumption chart for a user with optional date range and step
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

# Paywalled endpoint to get aggregated chart data for all users using manual x402 for BSV payments
@meter_router.get("/chart/users")
async def get_users_chart(request: Request):
    # Define payment requirements for x402 protocol
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
    
    # Check for X-PAYMENT header
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
    
    # Decode and validate payment header
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
    
    # Validate the BSV transaction
    if not await WhatsOnChainUtils.validate_transaction(txid, "12HKnZrJ8Fcx2F8SgJHUrV9uvGNo4eoveD", 100):
        return JSONResponse(
            content={
                "x402Version": 1,
                "accepts": [payment_requirements],
                "error": "Invalid or unconfirmed transaction"
            },
            status_code=402
        )
    
    # Aggregate data across all users
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