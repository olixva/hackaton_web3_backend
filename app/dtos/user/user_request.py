from pydantic import BaseModel, EmailStr, ConfigDict


class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
            }
        }
    )