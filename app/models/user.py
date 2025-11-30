from app.models.base_model import Model
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserWallet(BaseModel):
    """Embedded model for user's BSV wallet information."""
    bsv_address: str
    bsv_public_key: str
    encrypted_wif: str
    balance_satoshis: int = 0
    balance_euro: float = 0.0


class User(Model):
    """User document model with personal and wallet information."""
    name: str
    email: EmailStr
    created_at: datetime
    user_wallet: UserWallet
    profile_image_url: str | None = None
    tariff: float = 0.15
    preferred_currency: str = "EUR"

    class Settings:
        name = "users"
