from datetime import datetime
from pydantic import BaseModel

# Response model for meter creation, returning the created entry ID
class CreateMeterResponse(BaseModel):
    id: str

# Model for individual chart data points, containing timestamp, price, and kWh
class ChartItem(BaseModel):
    timestamp: datetime
    price: float
    kw: float

# Response model for chart generation, containing a list of chart items
class GenerateChartMeterResponse(BaseModel):
    chart: list[ChartItem]