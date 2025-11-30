from datetime import datetime, timedelta
from beanie import PydanticObjectId
from fastapi import HTTPException
from typing import Any

# DTOs
from app.dtos.meter.meter_response import CreateMeterResponse
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_response import ChartItem
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_request import StepEnum
# Models
from app.models.meter_reading import MeterReading
from app.models.user import User
from app.models.alarm import AlarmType
# Services
from app.services.alarm_service import AlarmService


class MeterService:

    @staticmethod
    async def create_meter(request: CreateMeterRequest) -> CreateMeterResponse:
        if not MeterReading.is_valid_id(request.user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # TODO: Try to pay if we cant possible default
        if not request.payment_id:
            ## Possible defaulter case, allow None
            pass

        # Get user for tariff
        user = await User.find_one({"_id": PydanticObjectId(request.user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create new meter reading
        kw_consumed = request.reading
        cost_euro = request.cost_euro or (kw_consumed * user.tariff)

        new_meter = MeterReading(
            user_id=PydanticObjectId(request.user_id),
            kw_consumed=kw_consumed,
            cost_euro=cost_euro,
            meter_id=request.meter_id,
            payment_id=PydanticObjectId(request.payment_id) if request.payment_id else None,
            timestamp=datetime.now(),
        )
        await new_meter.insert()

        # Check if alarms are triggered
        alarms = await AlarmService.get_alarms_by_user(request.user_id)
        for alarm in alarms:
            price = kw_consumed * user.tariff
            if await AlarmService.is_triggered(alarm, price=price, kw=kw_consumed):
                # Log alarm if triggered
                await AlarmService.log_alarm_history(
                    user_id=request.user_id,
                    alarm_id=str(alarm.id),
                    value=kw_consumed if alarm.type == AlarmType.ENERGY else price
                )

        return CreateMeterResponse(id=str(new_meter.id))
    
    @staticmethod
    async def generate_chart(
        user_id: str,
        start_date: str | None = None,
        end_date: str | None = None,
        step: StepEnum = StepEnum.DAILY
    ) -> GenerateChartMeterResponse:
        # Set default dates if not provided
        now = datetime.now()
        if start_date is None:
            default_periods = {
                StepEnum.HOURLY: timedelta(hours=24),
                StepEnum.DAILY: timedelta(days=30),
                StepEnum.WEEKLY: timedelta(weeks=4),
                StepEnum.MONTHLY: timedelta(days=365),  # approx 12 months
            }
            period = default_periods.get(step, timedelta(days=30))
            start_date = (now - period).isoformat()
        if end_date is None:
            end_date = now.isoformat()
        
        # Get user for tariff
        user = await User.find_one({"_id": PydanticObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        tariff = user.tariff
        
        # Build match stage
        match_stage = MeterService._build_match_stage(
            start_date, 
            end_date, 
            user_id
        )
        
        # Start pipeline with match
        pipeline = [{"$match": match_stage}]
        
        # Build group stage based on step
        if step == StepEnum.MONTHLY:
            MeterService._build_monthly_pipeline(pipeline)
        elif step == StepEnum.DAILY:
            MeterService._build_daily_pipeline(pipeline)
        elif step == StepEnum.WEEKLY:
            MeterService._build_weekly_pipeline(pipeline)
        elif step == StepEnum.HOURLY:
            MeterService._build_hourly_pipeline(pipeline)
        
        # Execute aggregation
        results = await MeterReading.aggregate(pipeline).to_list()
        
        # Calculate price using user's tariff
        for result in results:
            result["price"] = result["kw"] * tariff
        
        # Convert to ChartItem
        chart_data = [
            ChartItem(timestamp=result["timestamp"], kw=result["kw"], price=result["price"])
            for result in results
        ]
        
        return GenerateChartMeterResponse(chart=chart_data)

    @staticmethod
    def _build_monthly_pipeline(pipeline: list):
        group_id = {"year": {"$year": "$timestamp"}, "month": {"$month": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {"$project": {
                "timestamp": {
                    "$dateFromParts": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "day": 1
                    }
                },
                "kw": 1,
            }}
        ])

    @staticmethod
    def _build_daily_pipeline(pipeline: list):
        group_id = {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id": 1}},
            {"$project": {
                "timestamp": {"$dateFromString": {"dateString": "$_id"}},
                "kw": 1,
            }}
        ])

    @staticmethod
    def _build_weekly_pipeline(pipeline: list):
        group_id = {"year": {"$year": "$timestamp"}, "week": {"$week": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id.year": 1, "_id.week": 1}},
            {"$project": {
                "timestamp": {
                    "$dateFromParts": {
                        "isoWeekYear": "$_id.year",
                        "isoWeek": "$_id.week",
                        "isoDayOfWeek": 1 
                    }
                },
                "kw": 1,
            }}
        ])

    @staticmethod
    def _build_hourly_pipeline(pipeline: list):
        group_id = {"$dateToString": {"format": "%Y-%m-%d %H", "date": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id": 1}},
            {"$project": {
                "timestamp": {"$dateFromString": {"dateString": {"$concat": ["$_id", ":00:00"]}}},
                "kw": 1,
            }}
        ])

    @staticmethod
    def _build_match_stage(
        start_date: str | None, 
        end_date: str | None, 
        user_id: str
    ) -> dict[str, Any]:
        match_stage: dict[str, Any] = {"user_id": PydanticObjectId(user_id)}
        if start_date:
            match_stage["timestamp"] = {"$gte": datetime.fromisoformat(start_date)}
        if end_date:
            date_end_date = datetime.fromisoformat(end_date)
            if "timestamp" in match_stage:
                match_stage["timestamp"]["$lte"] = date_end_date
            else:
                match_stage["timestamp"] = {"$lte": date_end_date}
        return match_stage