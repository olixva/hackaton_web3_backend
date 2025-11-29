from datetime import datetime
from fastapi import HTTPException
from pydantic import EmailStr

# DTOs
from app.dtos.user.user_response import GetUserResponse
from app.dtos.user.user_response import CreateUserResponse
from app.dtos.user.user_request import CreateUserRequest
# Models
from app.models.user import User
from beanie import PydanticObjectId
# Wallet
from app.services.wallet_service import WalletService


class UserService:

    @staticmethod
    async def get_user(user_id: str) -> GetUserResponse:
        if not User.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return GetUserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email,
            bsv_address=user.user_wallet.bsv_address,
            profile_image_url=user.profile_image_url,
        )

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