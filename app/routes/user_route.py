from fastapi import APIRouter

# DTOs
from app.dtos.user.user_response import GetUserResponse
from app.dtos.user.user_response import CreateUserResponse
# Services
from app.services.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/user/{user_id}", response_model=GetUserResponse)
async def get_user(user_id: str):
    return await UserService.get_user(user_id=user_id)

@user_router.post("/user", response_model=CreateUserResponse)
async def create_user(name: str, email: str):
    return await UserService.create_user(name=name, email=email)