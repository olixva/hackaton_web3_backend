from datetime import datetime
from fastapi import HTTPException
from beanie import PydanticObjectId
from cachetools import TTLCache

# Import alarm and history models, and alarm type enum
from app.models.alarm import Alarm
from app.models.alarm_history import AlarmHistory
from app.models.alarm import AlarmType

# Import DTOs for request and response
from app.dtos.alarm.alarm_request import CreateAlarmRequest
from app.dtos.alarm.alarm_response import CreateAlarmResponse

# Cache for temporary storage with TTL
cache = TTLCache(maxsize=100, ttl=300)

# AlarmService class handles all alarm-related business logic
class AlarmService:

    # Create a new alarm for a user
    @staticmethod
    async def create_alarm(request: CreateAlarmRequest) -> CreateAlarmResponse:
        if not Alarm.is_valid_id(request.user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        new_alarm = Alarm(
            user_id=PydanticObjectId(request.user_id),
            type=request.type,
            threshold=request.threshold,
            active=request.active,
        )
        await new_alarm.insert()

        return CreateAlarmResponse(id=str(new_alarm.id))

    # Delete an alarm by ID
    @staticmethod
    async def delete_alarm(alarm_id: str) -> None:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        await alarm.delete()

    # Retrieve an alarm by ID
    @staticmethod
    async def get_alarm(alarm_id: str) -> Alarm:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        return alarm

    # Toggle the active status of an alarm
    @staticmethod
    async def toggle_alarm_active(alarm_id: str) -> None:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        alarm.active = not alarm.active
        await alarm.save()

    # Get all alarms for a specific user
    @staticmethod
    async def get_alarms_by_user(user_id: str) -> list[Alarm]:

        if not Alarm.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        return await Alarm.find({"user_id": PydanticObjectId(user_id)}).to_list()
    
    # Check if an alarm is triggered based on price or energy values
    @staticmethod
    async def is_triggered(alarm: Alarm, price: float, kw: float) -> bool:
        if not alarm.active:
            return False
        
        if alarm.type == AlarmType.MONEY:
            if price < alarm.threshold:
                return False
            return True

        elif alarm.type == AlarmType.ENERGY:
            if kw < alarm.threshold:
                return False
            return True
        
        return False
    
    # Get alarm history for a user
    @staticmethod
    async def get_alarms_history(user_id: str) -> list[AlarmHistory]:
        if not Alarm.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        return await AlarmHistory.find({"user_id": PydanticObjectId(user_id)}).to_list()

    # Log a new alarm trigger event in history
    @staticmethod
    async def log_alarm_history(user_id: str, alarm_id: str, value: float) -> None:
        if not Alarm.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        new_history = AlarmHistory(
            user_id=PydanticObjectId(user_id),
            alarm_id=PydanticObjectId(alarm_id),
            value=value,
            triggered_at=datetime.now(),
        )
        await new_history.insert()

    # Delete a specific alarm history entry
    @staticmethod
    async def delete_alarm_history(history_id: str) -> None:
        if not AlarmHistory.is_valid_id(history_id):
            raise HTTPException(status_code=400, detail="Invalid history ID format")

        history = await AlarmHistory.find_one(AlarmHistory.id == PydanticObjectId(history_id))
        if not history:
            raise HTTPException(status_code=404, detail="Alarm history not found")

        await history.delete()
