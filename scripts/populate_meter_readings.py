import asyncio
from datetime import datetime, timedelta
from app.config.mongo import MongoDbClient
from app.models.meter_reading import MeterReading
from beanie import PydanticObjectId


async def populate_meter_readings():
    # Initialize the database client
    client = MongoDbClient()
    await client.init()

    # Sample user ID (use an existing user ID or create one)
    user_id = PydanticObjectId("692b2e7deed34135d7cf5a8c")  # Example ObjectId

    # Sample meter ID
    meter_id = "meter_001"

    # Generate sample readings for the past 12 months
    base_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    base_reading = 1000.0  # Starting meter reading

    readings = []
    for i in range(12):
        # Calculate date for this month
        reading_date = base_date - timedelta(days=30 * (11 - i))

        # Simulate increasing consumption (more in winter, less in summer)
        month = reading_date.month
        if month in [12, 1, 2]:  # Winter
            consumption = 180.0
        elif month in [6, 7, 8]:  # Summer
            consumption = 80.0
        else:  # Spring/Fall
            consumption = 120.0

        # Accumulate reading
        base_reading += consumption

        # Create MeterReading document
        reading = MeterReading(
            user_id=user_id,
            meter_id=meter_id,
            reading=round(base_reading, 2),
            kw_consumed=round(consumption, 2),
            timestamp=reading_date,
            payment_id=None  # No payment for sample data
        )
        readings.append(reading)

    # Insert all readings
    inserted_readings = await MeterReading.insert_many(readings)

    print(f"Inserted {len(inserted_readings.inserted_ids)} meter readings into the database.")

    # Close the client
    await client.close()


if __name__ == "__main__":
    asyncio.run(populate_meter_readings())