# Import standard libraries for datetime handling, system operations, HTTP requests, and async programming
from datetime import datetime
import sys
import os
import httpx

# Add the project root to the Python path to enable imports from the app directory
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio

# SimulateMeter class: Manages meter properties, simulates hourly energy consumption, and posts readings to the backend API
class SimulateMeter:
    """
    This simulation represents a smart meter that periodically sends consumption data to our API,
    triggering automatic BSV payments based on the calculated energy cost and user's tariff.
    """

    # Define static meter properties
    meter_id = "meter_001"
    base_hourly_kwh = 0.75

    # Post meter readings to the backend via HTTP
    async def post_meter_reading(self, kw: float):
        url = "https://hackaton-web3-backend.vercel.app/meter"
        data = {
            "user_id": "692b9e2c0c45d7f4031812c4",
            "meter_id": self.meter_id,
            "reading": kw,
        }
        try:
            # Send POST request with 30-second timeout to handle potential cold starts
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data)
                print(f"📡 HTTP Response: {response.status_code}")
                # Log response body for error debugging
                if response.status_code >= 400:
                    print(f"❌ Response body: {response.text}")
                response.raise_for_status()
        except Exception as e:
            print(f"❌ Error posting meter reading: {type(e).__name__}: {e}")
            raise

    def simulate_hourly_kwh(self, ts: datetime) -> float:
        """
        Simulate hourly kWh consumption based on time patterns and seasonality.
        - Peak consumption: 18:00–22:00 (evening).
        - Secondary peak: 7:00–9:00 (morning).
        - Low consumption: 00:00–06:00 (night).
        - Seasonal variation: Higher in winter, lower in summer.
        - Random noise: ±20% variation.
        """
        import random

        hour = ts.hour
        month = ts.month

        # Determine hourly consumption factor based on time of day
        if 0 <= hour < 6:
            hour_factor = 0.3  # Night: low consumption
        elif 6 <= hour < 9:
            hour_factor = 1.2  # Morning peak
        elif 9 <= hour < 17:
            hour_factor = 0.7  # Day: moderate consumption
        elif 17 <= hour < 22:
            hour_factor = 1.7  # Evening peak
        else:  # 22-24
            hour_factor = 0.9  # Late evening: moderate

        # Apply seasonal adjustment
        if month in (12, 1, 2):      # Winter months
            season_factor = 1.3
        elif month in (6, 7, 8):     # Summer months
            season_factor = 0.8
        else:                        # Spring/Autumn
            season_factor = 1.0

        # Add random noise for realism (±20%)
        noise = random.uniform(0.8, 1.2)

        # Calculate final kWh, ensuring minimum consumption
        kw = self.base_hourly_kwh * hour_factor * season_factor * noise
        return max(kw, self.base_hourly_kwh * 0.1)

# Main asynchronous function: Runs the continuous meter simulation loop
async def main():
    simulator = SimulateMeter()
    print("🚀 Starting meter simulation in background...")
    print("📊 Simulating hourly readings.\n")

    try:
        # Infinite loop to simulate continuous meter readings
        while True:
            now = datetime.now()
            # Generate simulated kWh for current hour
            kw = simulator.simulate_hourly_kwh(now)
            # Post the reading to the backend API
            await simulator.post_meter_reading(kw)
            print(f"✅ [{now.strftime('%Y-%m-%d %H:%M:%S')}] Reading sent: {kw:.2f} kWh (hour: {now.hour})")
            print("⏳ Waiting 1 hour for next simulation...\n")
            # Sleep for 20 seconds (for testing; in production, use 3600 for 1 hour)
            await asyncio.sleep(20)
    except Exception as e:
        print(f"❌ Simulation error: {e}")

# Entry point: Run the main function with asyncio
if __name__ == "__main__":
    asyncio.run(main())