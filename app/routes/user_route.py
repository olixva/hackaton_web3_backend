from fastapi import APIRouter

# Models
from app.dtos.user.user_response import GetUserResponse

# Services
from app.services.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/user/{user_id}", response_model=GetUserResponse)
async def get_user(user_id: str | None = None):
    return await UserService.get_user(user_id="1")