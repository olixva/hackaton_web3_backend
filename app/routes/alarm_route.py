from fastapi import APIRouter

# Import DTOs for alarm request and response models
from app.dtos.alarm.alarm_request import CreateAlarmRequest
from app.dtos.alarm.alarm_response import CreateAlarmResponse
from app.dtos.alarm.alarm_response import GetAlarmResponse
from app.dtos.alarm.alarm_response import AlarmHistoryResponse

# Import alarm service for handling business logic
from app.services.alarm_service import AlarmService

# Create router for alarm-related endpoints with prefix and tags
alarm_router = APIRouter(prefix="/alarm", tags=["alarm"])

# Endpoint to create a new alarm
@alarm_router.post("", response_model=CreateAlarmResponse)
async def create_alarm(request: CreateAlarmRequest):
    return await AlarmService.create_alarm(request)

# Endpoint to delete an alarm by ID
@alarm_router.delete("/{alarm_id}")
async def delete_alarm(alarm_id: str):
    await AlarmService.delete_alarm(alarm_id)
    return {"message": "Alarm deleted"}

# Endpoint to retrieve a specific alarm by ID
@alarm_router.get("/{alarm_id}", response_model=GetAlarmResponse)
async def get_alarm(alarm_id: str):
    alarm = await AlarmService.get_alarm(alarm_id)
    return GetAlarmResponse(
        id=str(alarm.id),
        user_id=str(alarm.user_id),
        type=alarm.type,
        threshold=alarm.threshold,
        active=alarm.active,
    )

# Endpoint to toggle the active status of an alarm
@alarm_router.patch("/{alarm_id}/toggle", status_code=204)
async def toggle_alarm_active(alarm_id: str):
    await AlarmService.toggle_alarm_active(alarm_id)

# Endpoint to get all alarms for a specific user
@alarm_router.get("/user/{user_id}", response_model=list[GetAlarmResponse])
async def get_alarms_by_user(user_id: str):
    alarms = await AlarmService.get_alarms_by_user(user_id)
    return [
        GetAlarmResponse(
            id=str(alarm.id),
            user_id=str(alarm.user_id),
            type=alarm.type,
            threshold=alarm.threshold,
            active=alarm.active,
        ) for alarm in alarms
    ]

# Endpoint to get alarm history for a user
@alarm_router.get("/history/{user_id}", response_model=list[AlarmHistoryResponse])
async def get_alarms_history(user_id: str):
    history = await AlarmService.get_alarms_history(user_id)
    return [
        AlarmHistoryResponse(
            id=str(h.id),
            user_id=str(h.user_id),
            alarm_id=str(h.alarm_id),
            value=h.value,
            triggered_at=h.triggered_at
        ) for h in history
    ]

# Endpoint to delete a specific alarm history entry
@alarm_router.delete("/history/{history_id}")
async def delete_alarm_history(history_id: str):
    await AlarmService.delete_alarm_history(history_id)
    return {"message": "Alarm history deleted"}