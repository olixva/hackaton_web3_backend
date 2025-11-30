from pydantic import BaseModel, ConfigDict

# Response model for getting user details, including wallet balance and usage
class GetUserResponse(BaseModel):
    """Response model for retrieving user information."""
    # Base fields
    id: str
    name: str
    email: str
    # Wallet
    bsv_address: str | None = None
    balance_satoshis: int | None = None
    balance_euro: float | None = None
    # Image
    profile_image_url: str | None = None
    # Monthly usage
    monthly_usage_kwh: float | None = None

    model_config = ConfigDict(from_attributes=True)

# Response model for user creation, returning the new user ID
class CreateUserResponse(BaseModel):
    """Response model for user creation."""
    id: str

    model_config = ConfigDict(from_attributes=True)