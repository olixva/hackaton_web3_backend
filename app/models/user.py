from beanie import Document
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserWallet(BaseModel):
    bsv_address: str
    bsv_pubkey: str
    encrypted_wif: str


class User(Document):
    name: str
    email: EmailStr
    created_at: datetime
    user_wallet: UserWallet

    class Settings:
        name = "users"