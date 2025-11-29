import asyncio
from datetime import datetime, timedelta
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from beanie import PydanticObjectId
from app.config.mongo import MongoDbClient
from app.models.meter_reading import MeterReading


async def generate_simple_readings() -> None:
    client = MongoDbClient()
    await client.init()

    user_object_id = PydanticObjectId("692b566e0ef3a85601b288f2")
    meter_id = "meter_001"

    end = datetime.now().replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=30)

    readings = []
    t = start
    total_hours = 30 * 24
    for _ in range(total_hours):
        value = round(random.uniform(10, 100), 3)
        readings.append(
            MeterReading(
                user_id=user_object_id,
                meter_id=meter_id,
                kw_consumed=value,
                timestamp=t,
                payment_id=None,
            )
        )
        t += timedelta(hours=1)

    if readings:
        await MeterReading.insert_many(readings)

    await client.close()


if __name__ == "__main__":
    asyncio.run(generate_simple_readings())
