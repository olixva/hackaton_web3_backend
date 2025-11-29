from pydantic import BaseModel


class CreateMeterResponse(BaseModel):
    id: str
