from datetime import datetime
from fastapi import HTTPException

# Import DTOs for user requests and responses
from app.dtos.user.user_response import GetUserResponse
from app.dtos.user.user_response import CreateUserResponse
from app.dtos.user.user_request import CreateUserRequest
from app.dtos.user.user_request import PatchUserRequest
# Import User model
from app.models.user import User
# Import Beanie for ObjectId
from beanie import PydanticObjectId
# Import services for wallet, meter, and WhatsOnChain
from app.services.wallet_service import WalletService
from app.services.meter_service import MeterService
from app.utils.whatsonchain_utils import WhatsOnChainUtils


class UserService:

    # Retrieve user details including wallet balance and monthly usage
    @staticmethod
    async def get_user(user_id: str) -> GetUserResponse:
        # Check if ID format is valid
        if not User.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # Get user from database
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get wallet balance
        balance_satoshis = None
        balance_euro = None
        if user.user_wallet and user.user_wallet.bsv_address:
            balance_satoshis = await WhatsOnChainUtils.get_balance(user.user_wallet.bsv_address)
            balance_euro = await WhatsOnChainUtils.convert_satoshis_to_euro(balance_satoshis)
            # Update the user wallet
            user.user_wallet.balance_satoshis = balance_satoshis
            user.user_wallet.balance_euro = balance_euro
            await user.save()

        # Calculate monthly usage
        monthly_usage_kwh = await MeterService.get_monthly_usage_kwh(user_id)
        
        # Return user details in response model
        return GetUserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            bsv_address=user.user_wallet.bsv_address if user.user_wallet else None,
            balance_satoshis=balance_satoshis,
            balance_euro=balance_euro,
            monthly_usage_kwh=monthly_usage_kwh,
            profile_image_url=user.profile_image_url,
        )

    # Create a new user with a generated wallet
    @staticmethod
    async def create_user(request: CreateUserRequest) -> CreateUserResponse:
        new_wallet = WalletService.create_wallet()
        new_user = User(
            name=request.name,
            email=request.email,
            created_at=datetime.now(),
            user_wallet=new_wallet,
        )

        await new_user.insert()

        return CreateUserResponse(id=str(new_user.id))

    # Update user settings like tariff and currency
    @staticmethod
    async def patch_user(user_id: str, request: PatchUserRequest) -> GetUserResponse:
        # Check if ID format is valid
        if not User.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # Get user from database
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update user tariff and preferred currency
        if request.tariff is not None:
            user.tariff = request.tariff
        if request.preferred_currency is not None:
            user.preferred_currency = request.preferred_currency

        # Save changes to database
        await user.save()

        # Return updated user details
        return GetUserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            bsv_address=user.user_wallet.bsv_address,
            balance_satoshis=user.user_wallet.balance_satoshis if user.user_wallet else None,
            balance_euro=user.user_wallet.balance_euro if user.user_wallet else None,
            profile_image_url=user.profile_image_url,
        )