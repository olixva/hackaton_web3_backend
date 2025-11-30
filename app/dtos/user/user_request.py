from pydantic import BaseModel, EmailStr, ConfigDict

# Request model for creating a new user with basic profile information
class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    name: str
    email: EmailStr
    profile_image_url : str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "profile_image_url": "https://example.com/profile.jpg"
            }
        }
    )

# Request model for patching/updating user settings like tariff and currency
class PatchUserRequest(BaseModel):
    """Request model for updating user settings."""
    tariff: float | None = None
    preferred_currency: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tariff": 0.20,
                "preferred_currency": "USD"
            }
        }
    )