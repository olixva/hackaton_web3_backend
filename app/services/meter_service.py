from datetime import datetime
from fastapi import HTTPException
from typing import Any

# DTOs
from app.dtos.meter.meter_response import CreateMeterResponse
from app.dtos.meter.meter_response import GenerateChartMeterResponse
from app.dtos.meter.meter_response import ChartItem
from app.dtos.meter.meter_request import CreateMeterRequest
from app.dtos.meter.meter_request import GenerateChartMeterRequest
from app.dtos.meter.meter_request import StepEnum
# Models
from app.models.meter_reading import MeterReading
from beanie import PydanticObjectId


class MeterService:

    @staticmethod
    async def create_meter(request: CreateMeterRequest) -> CreateMeterResponse:
        if not MeterReading.is_valid_id(request.user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        if not request.payment_id:
            raise HTTPException(status_code=400, detail="Not paid yet")

        if not MeterReading.is_valid_id(request.payment_id):
            raise HTTPException(status_code=400, detail="Invalid payment ID format")

        new_meter = MeterReading(
            user_id=PydanticObjectId(request.user_id),
            kw_consumed=request.reading, # TODO: Calculate kw_consumed based on previous reading
            meter_id=request.meter_id,
            reading=request.reading,
            payment_id=PydanticObjectId(request.payment_id) if request.payment_id else None,
            timestamp=datetime.now(),
        )
        await new_meter.insert()

        return CreateMeterResponse(id=str(new_meter.id))
    
    @staticmethod
    async def generate_chart(request: GenerateChartMeterRequest) -> GenerateChartMeterResponse:
        # Build match stage
        match_stage = MeterService._build_match_stage(
            request.start_date, 
            request.end_date, 
            request.user_id
        )
        
        # Start pipeline with match
        pipeline = [{"$match": match_stage}]
        
        # Build group stage based on step
        if request.step == StepEnum.MONTHLY:
            MeterService._build_monthly_pipeline(pipeline)
        elif request.step == StepEnum.DAILY:
            MeterService._build_daily_pipeline(pipeline)
        elif request.step == StepEnum.WEEKLY:
            MeterService._build_weekly_pipeline(pipeline)
        elif request.step == StepEnum.HOURLY:
            MeterService._build_hourly_pipeline(pipeline)
        
        # Execute aggregation
        results = await MeterReading.aggregate(pipeline).to_list()
        
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
            "price": {"$sum": {"$multiply": ["$kw_consumed", 0.5]}}
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
                "price": 1
            }}
        ])

    @staticmethod
    def _build_daily_pipeline(pipeline: list):
        group_id = {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
            "price": {"$sum": {"$multiply": ["$kw_consumed", 0.5]}}
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id": 1}},
            {"$project": {
                "timestamp": {"$dateFromString": {"dateString": "$_id"}},
                "kw": 1,
                "price": 1
            }}
        ])

    @staticmethod
    def _build_weekly_pipeline(pipeline: list):
        group_id = {"year": {"$year": "$timestamp"}, "week": {"$week": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
            "price": {"$sum": {"$multiply": ["$kw_consumed", 0.5]}}
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
                "price": 1
            }}
        ])

    @staticmethod
    def _build_hourly_pipeline(pipeline: list):
        group_id = {"$dateToString": {"format": "%Y-%m-%d %H", "date": "$timestamp"}}
        group_stage = {
            "_id": group_id,
            "kw": {"$sum": "$kw_consumed"},
            "price": {"$sum": {"$multiply": ["$kw_consumed", 0.5]}}
        }
        pipeline.extend([
            {"$group": group_stage},
            {"$sort": {"_id": 1}},
            {"$project": {
                "timestamp": {"$dateFromString": {"dateString": {"$concat": ["$_id", ":00:00"]}}},
                "kw": 1,
                "price": 1
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