from fastapi import HTTPException

from app.dtos.user.user_response import GetUserResponse
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
    