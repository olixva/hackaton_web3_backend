from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUserRequest(BaseModel):
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