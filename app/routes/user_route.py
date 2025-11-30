from fastapi import APIRouter

# DTOs
from app.dtos.user.user_response import GetUserResponse
from app.dtos.user.user_response import CreateUserResponse
from app.dtos.user.user_request import CreateUserRequest
from app.dtos.user.user_request import PatchUserRequest
# Services
from app.services.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/{user_id}", response_model=GetUserResponse)
async def get_user(user_id: str):
    return await UserService.get_user(user_id=user_id)

@user_router.post("", response_model=CreateUserResponse)
async def create_user(request: CreateUserRequest):
    return await UserService.create_user(request)

@user_router.patch("/{user_id}", response_model=GetUserResponse)
async def patch_user(user_id: str, request: PatchUserRequest):
    return await UserService.patch_user(user_id, request)