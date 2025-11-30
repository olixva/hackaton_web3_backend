from datetime import datetime
from fastapi import HTTPException
from beanie import PydanticObjectId
from cachetools import cached, TTLCache

from app.models.alarm import Alarm
from app.models.alarm_history import AlarmHistory
from app.models.alarm import AlarmType

from app.dtos.alarm.alarm_request import CreateAlarmRequest
from app.dtos.alarm.alarm_response import CreateAlarmResponse

cache = TTLCache(maxsize=100, ttl=300)


class AlarmService:

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

    @staticmethod
    async def delete_alarm(alarm_id: str) -> None:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        await alarm.delete()

    @staticmethod
    async def get_alarm(alarm_id: str) -> Alarm:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        return alarm

    @staticmethod
    async def toggle_alarm_active(alarm_id: str) -> None:
        if not Alarm.is_valid_id(alarm_id):
            raise HTTPException(status_code=400, detail="Invalid alarm ID format")

        alarm = await Alarm.find_one(Alarm.id == PydanticObjectId(alarm_id))
        if not alarm:
            raise HTTPException(status_code=404, detail="Alarm not found")

        alarm.active = not alarm.active
        await alarm.save()

    @staticmethod
    async def get_alarms_by_user(user_id: str) -> list[Alarm]:

        if not Alarm.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        return await Alarm.find({"user_id": PydanticObjectId(user_id)}).to_list()
    
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
    
    @staticmethod
    async def get_alarms_history(user_id: str) -> list[AlarmHistory]:
        if not Alarm.is_valid_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        return await AlarmHistory.find({"user_id": PydanticObjectId(user_id)}).to_list()

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
