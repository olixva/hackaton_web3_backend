import asyncio
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add the project root to the Python path to enable imports from the app directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from beanie import PydanticObjectId

from app.config.mongo import MongoDbClient
from app.models.meter_reading import MeterReading

# Asynchronous function to populate hourly meter readings for a user
async def populate_hourly_meter_readings(
    user_id: str,
    meter_id: str = "meter_001",
    days: int = 30,
    avg_daily_kwh: float = 15.0,
    clear_existing: bool = True,
    end_datetime: Optional[datetime] = None,
) -> None:
    """
    Generates hourly consumption readings for a single user.

    - user_id: ObjectId of the user (string).
    - meter_id: meter identifier.
    - days: number of days back from end_datetime (default, now).
    - avg_daily_kwh: expected average daily consumption in kWh.
    - clear_existing: if True, deletes previous readings of that user/meter in the range.
    - end_datetime: end of the simulation range (default, datetime.now rounded to hour).
    """

    client = MongoDbClient()
    await client.init()

    user_oid = PydanticObjectId(user_id)

    if end_datetime is None:
        end_datetime = datetime.now().replace(minute=0, second=0, microsecond=0)
    else:
        end_datetime = end_datetime.replace(minute=0, second=0, microsecond=0)

    start_datetime = end_datetime - timedelta(days=days)

    if clear_existing:
        await MeterReading.find(
            {
                "user_id": user_oid,
                "meter_id": meter_id,
                "timestamp": {"$gte": start_datetime, "$lte": end_datetime},
            }
        ).delete_many()

    total_hours = int((end_datetime - start_datetime).total_seconds() // 3600)
    if total_hours <= 0:
        print("Invalid date range, no data generated.")
        await client.close()
        return

    base_hourly_kwh = avg_daily_kwh / 24.0

    readings: list[MeterReading] = []
    current_time = start_datetime

    for _ in range(total_hours + 1):
        kw = _simulate_hourly_kwh(current_time, base_hourly_kwh)

        reading_doc = MeterReading(
            user_id=user_oid,
            meter_id=meter_id,
            kw_consumed=round(kw, 3),
            timestamp=current_time,
        )
        readings.append(reading_doc)

        current_time += timedelta(hours=1)

    if readings:
        res = await MeterReading.insert_many(readings)
        print(f"Inserted {len(res.inserted_ids)} hourly readings.")
    else:
        print("No readings inserted.")

    await client.close()

# Helper function to simulate hourly kWh consumption
def _simulate_hourly_kwh(ts: datetime, base_hourly_kwh: float) -> float:
    """
    Simple simulation:
    - More consumption 18:00–22:00.
    - Secondary peak 7:00–9:00.
    - Less consumption at night.
    - Winter consumes a bit more, summer a bit less.
    - A bit of random noise.
    """
    import random

    hour = ts.hour
    month = ts.month

    # Very simple hourly profile
    if 0 <= hour < 6:
        hour_factor = 0.3
    elif 6 <= hour < 9:
        hour_factor = 1.2
    elif 9 <= hour < 17:
        hour_factor = 0.7
    elif 17 <= hour < 22:
        hour_factor = 1.7
    else:  # 22-24
        hour_factor = 0.9

    # Very simple seasonality
    if month in (12, 1, 2):      # winter
        season_factor = 1.3
    elif month in (6, 7, 8):     # summer
        season_factor = 0.8
    else:                        # spring / autumn
        season_factor = 1.0

    # Random noise ±20%
    noise = random.uniform(0.8, 1.2)

    kw = base_hourly_kwh * hour_factor * season_factor * noise
    return max(kw, base_hourly_kwh * 0.1)

# Main asynchronous function to run the population script
async def main():
    # Change this ID to a real one from your database
    user_id = "692b9e2c0c45d7f4031812c4"
    meter_id = "meter_001"

    await populate_hourly_meter_readings(
        user_id=user_id,
        meter_id=meter_id,
        days=60,
        avg_daily_kwh=18,
        clear_existing=True,
    )

# Entry point to run the script
if __name__ == "__main__":
    asyncio.run(main())
