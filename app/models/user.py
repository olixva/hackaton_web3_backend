<<<<<<< HEAD
from beanie import Document
=======
from beanie import Document, PydanticObjectId
from pydantic import EmailStr
>>>>>>> de72181 (feat: implement user retrieval service and response model)
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
<<<<<<< HEAD
        name = "users"
=======
        name = "users"

    @staticmethod
    def is_valid_id(id) -> bool:
        try:
            PydanticObjectId(id)
        except Exception:
            return False
        return True
>>>>>>> de72181 (feat: implement user retrieval service and response model)
