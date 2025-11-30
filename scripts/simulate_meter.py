from datetime import datetime
import sys
import os
import httpx

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio


class SimulateMeter:

    # Define meter properties
    meter_id = "meter_001"
    base_hourly_kwh = 0.75

    # Post meter readings to the backend via HTTP
    async def post_meter_reading(self, kw: float):
        url = "https://hackaton-web3-backend.vercel.app//meter"
        data = {
            "user_id": "692b9e2c0c45d7f4031812c4",
            "meter_id": self.meter_id,
            "reading": kw,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            print(f"📡 HTTP Response: {response.status_code}")

    def simulate_hourly_kwh(self, ts: datetime) -> float:
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

        kw = self.base_hourly_kwh * hour_factor * season_factor * noise
        return max(kw, self.base_hourly_kwh * 0.1)


async def main():
    simulator = SimulateMeter()
    print("🚀 Iniciando simulación de medidor en segundo plano...")
    print("📊 Simulando lecturas cada hora.\n")

    try:
        while True:
            now = datetime.now()
            kw = simulator.simulate_hourly_kwh(now)
            await simulator.post_meter_reading(kw)
            print(f"✅ [{now.strftime('%Y-%m-%d %H:%M:%S')}] Lectura enviada: {kw:.2f} kWh (hora: {now.hour})")
            print("⏳ Esperando 1 hora para la siguiente simulación...\n")
            await asyncio.sleep(20)
    except Exception as e:
        print(f"❌ Error en simulación: {e}")


if __name__ == "__main__":
    asyncio.run(main())