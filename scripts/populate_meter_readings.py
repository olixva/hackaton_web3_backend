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


async def generate_hourly_meter_readings(
    user_id: str,
    meter_id: str = "meter_001",
    days: int = 30,
    start_from_now: bool = True,
    start_date: Optional[datetime] = None,
    initial_reading: float = 1000.0,
    avg_daily_kwh: float = 15.0,
) -> None:
    """
    Genera lecturas horarias de un contador para un único usuario.

    - user_id: string con el ObjectId del usuario.
    - meter_id: id del contador.
    - days: número de días hacia atrás que quieres simular.
    - start_from_now: si True, genera desde ahora hacia atrás 'days' días.
      Si False, se usa 'start_date' como fecha final del periodo.
    - start_date: fecha final del periodo (solo si start_from_now=False).
    - initial_reading: lectura inicial acumulada del contador (kWh).
    - avg_daily_kwh: consumo medio diario esperado (kWh/día).
    """

    # --- Inicializar BBDD ---
    client = MongoDbClient()
    await client.init()

    user_object_id = PydanticObjectId(user_id)

    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    if start_from_now:
        end_datetime = now
    else:
        if start_date is None:
            raise ValueError("Si start_from_now=False debes pasar start_date")
        end_datetime = start_date.replace(minute=0, second=0, microsecond=0)

    start_datetime = end_datetime - timedelta(days=days)
    
    # Por si quieres limpiar antes los datos de ese usuario/contador en el rango:
    await MeterReading.find(
        {
            "user_id": user_object_id,
            "meter_id": meter_id,
            "timestamp": {"$gte": start_datetime, "$lte": end_datetime},
        }
    ).delete_many()

    print(f"Generando datos desde {start_datetime} hasta {end_datetime} (horarios)")

    total_hours = int((end_datetime - start_datetime).total_seconds() // 3600)
    if total_hours <= 0:
        print("Rango de fechas inválido, no se generan datos.")
        await client.close()
        return

    # Consumo medio horario aproximado a partir del diario
    base_hourly_kwh = avg_daily_kwh / 24.0

    readings = []
    cumulative_reading = initial_reading

    current_time = start_datetime

    for _ in range(total_hours + 1):
        # Perfil de consumo según hora del día y estación
        hourly_kwh = _simulate_hourly_consumption(current_time, base_hourly_kwh)

        cumulative_reading += hourly_kwh

        reading = MeterReading(
            user_id=user_object_id,
            meter_id=meter_id,
            reading=round(cumulative_reading, 3),   # lectura acumulada
            kw_consumed=round(hourly_kwh, 3),       # consumo en esa hora
            timestamp=current_time,
            payment_id=None,  # datos de ejemplo -> sin pago asociado
        )
        readings.append(reading)

        current_time += timedelta(hours=1)

    if readings:
        result = await MeterReading.insert_many(readings)
        print(f"Insertadas {len(result.inserted_ids)} lecturas horarias.")
    else:
        print("No hay lecturas que insertar.")

    await client.close()

def _simulate_hourly_consumption(ts: datetime, base_hourly_kwh: float) -> float:
    """
    Simula consumo horario con:
    - Picos de mañana y noche
    - Más consumo en invierno, menos en verano
    - Pequeña variación aleatoria
    """
    import math
    import random

    hour = ts.hour
    month = ts.month

    # Factor por franja horaria (perfil típico doméstico)
    if 0 <= hour < 6:
        hour_factor = 0.3  # madrugada
    elif 6 <= hour < 9:
        hour_factor = 1.3  # mañana (desayunos, duchas...)
    elif 9 <= hour < 17:
        hour_factor = 0.7  # horas de trabajo fuera de casa
    elif 17 <= hour < 22:
        hour_factor = 1.8  # tarde-noche, máximo consumo
    else:  # 22-24
        hour_factor = 0.9  # noche

    # Factor por estación (más calefacción en invierno, menos en verano)
    if month in [12, 1, 2]:       # invierno
        season_factor = 1.4
    elif month in [6, 7, 8]:      # verano
        season_factor = 0.8
    else:                         # primavera/otoño
        season_factor = 1.0

    # Ruido aleatorio suave +/- 20%
    noise_factor = random.uniform(0.8, 1.2)

    hourly_kwh = base_hourly_kwh * hour_factor * season_factor * noise_factor

    # Nunca negativo, ni ridículamente pequeño
    hourly_kwh = max(hourly_kwh, base_hourly_kwh * 0.1)

    return hourly_kwh

async def main():
    # Cambia este ID por uno real de tu BBDD
    user_id = "692b566e0ef3a85601b288f2"
    meter_id = "meter_001"

    # Ejemplo: generar 60 días hacia atrás desde ahora
    await generate_hourly_meter_readings(
        user_id=user_id,
        meter_id=meter_id,
        days=60,
        start_from_now=True,
        initial_reading=500.0,
        avg_daily_kwh=18.0,
    )


if __name__ == "__main__":
    asyncio.run(main())
