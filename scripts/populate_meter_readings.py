import asyncio
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from beanie import PydanticObjectId

from app.config.mongo import MongoDbClient
from app.models.meter_reading import MeterReading


async def populate_hourly_meter_readings(
    user_id: str,
    meter_id: str = "meter_001",
    days: int = 30,
    avg_daily_kwh: float = 15.0,
    clear_existing: bool = True,
    end_datetime: Optional[datetime] = None,
) -> None:
    """
    Genera lecturas horarias de consumo para un único usuario.

    - user_id: ObjectId del usuario (string).
    - meter_id: identificador del contador.
    - days: número de días hacia atrás desde end_datetime (por defecto, ahora).
    - avg_daily_kwh: consumo medio diario esperado en kWh.
    - clear_existing: si True, borra lecturas previas de ese usuario/contador en el rango.
    - end_datetime: fin del rango de simulación (por defecto, datetime.now redondeado a hora).
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
        print("Rango de fechas inválido, no se generan datos.")
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
            payment_id=None,   # datos de ejemplo -> sin pago asociado
        )
        readings.append(reading_doc)

        current_time += timedelta(hours=1)

    if readings:
        res = await MeterReading.insert_many(readings)
        print(f"Insertadas {len(res.inserted_ids)} lecturas horarias.")
    else:
        print("No se insertó ninguna lectura.")

    await client.close()


def _simulate_hourly_kwh(ts: datetime, base_hourly_kwh: float) -> float:
    """
    Simulación sencilla:
    - Más consumo 18:00–22:00.
    - Pico secundario 7:00–9:00.
    - Menos consumo de madrugada.
    - Invierno consume algo más, verano algo menos.
    - Un poco de ruido aleatorio.
    """
    import random

    hour = ts.hour
    month = ts.month

    # Perfil horario muy simple
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

    # Estación del año muy sencilla
    if month in (12, 1, 2):      # invierno
        season_factor = 1.3
    elif month in (6, 7, 8):     # verano
        season_factor = 0.8
    else:                        # primavera / otoño
        season_factor = 1.0

    # Ruido aleatorio ±20%
    noise = random.uniform(0.8, 1.2)

    kw = base_hourly_kwh * hour_factor * season_factor * noise
    return max(kw, base_hourly_kwh * 0.1)


async def main():
    # Cambia este ID por uno real de tu base de datos
    user_id = "692b566e0ef3a85601b288f2"
    meter_id = "meter_001"

    await populate_hourly_meter_readings(
        user_id=user_id,
        meter_id=meter_id,
        days=60,
        avg_daily_kwh=18,
        clear_existing=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
