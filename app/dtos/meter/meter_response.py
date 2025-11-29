from datetime import datetime
from pydantic import BaseModel


class CreateMeterResponse(BaseModel):
    id: str

class ChartItem(BaseModel):
    timestamp: datetime
    price: float
    kw: float

class GenerateChartMeterResponse(BaseModel):
    chart: list[ChartItem]