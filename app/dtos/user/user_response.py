from pydantic import BaseModel, ConfigDict


class GetUserResponse(BaseModel):
    # Base fields
    id: str
    name: str
    email: str
    # Wallet
    bsv_address: str | None = None
    # Image
    profile_image_url: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CreateUserResponse(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)