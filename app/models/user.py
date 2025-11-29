from app.models.base_model import Model
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserWallet(BaseModel):
    bsv_address: str
    bsv_pubkey: str
    encrypted_wif: str


class User(Model):
    name: str
    email: EmailStr
    bsv_address: str | None = None
    created_at: datetime
    user_wallet: UserWallet
    profile_image_url: str | None = None

    class Settings:
        name = "users"
