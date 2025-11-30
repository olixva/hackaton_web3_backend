from enum import Enum
from app.models.base_model import Model
from beanie import PydanticObjectId


class AlarmType(str, Enum):
    """Enumeration for alarm types."""
    MONEY = "money"
    ENERGY = "energy"


class Alarm(Model):
    """Alarm document model for user-defined thresholds."""
    user_id: PydanticObjectId
    threshold: float
    type: AlarmType
    active: bool

    class Settings:
        name = "alarms"
