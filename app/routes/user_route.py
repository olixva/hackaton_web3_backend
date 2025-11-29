from fastapi import APIRouter

# Models
from app.models.user import User

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/me", response_model=User)
async def me():
    return {"message": "User details"}