from datetime import datetime
from fastapi import HTTPException

# DTOs
from app.dtos.user.user_response import GetUserResponse
from app.dtos.user.user_response import CreateUserResponse
# Models
from app.models.user import UserWallet
from app.models.user import User
from beanie import PydanticObjectId


class UserService:

    @staticmethod
    async def get_user(user_id: str) -> GetUserResponse:
        if not User.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        user = await User.find_one(User.id == PydanticObjectId(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return GetUserResponse(id=str(user.id), name=user.name)
    
    @staticmethod
    async def create_user(name: str, email: str) -> CreateUserResponse:
        # TODO: Call wallet generation service

        new_user = User(
            name=name,
            email=email,
            created_at=datetime.now(),
            user_wallet=UserWallet(
                bsv_address="",
                bsv_pubkey="",
                encrypted_wif="",
            ),
        )
        await new_user.insert()

        return CreateUserResponse(id=str(new_user.id))