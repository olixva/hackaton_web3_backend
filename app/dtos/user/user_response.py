from pydantic import BaseModel, ConfigDict


class GetUserResponse(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class CreateUserResponse(BaseModel):
    id: str

    model_config = ConfigDict(from_attributes=True)