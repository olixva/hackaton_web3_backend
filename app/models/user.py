from beanie import Document
from pydantic import EmailStr
from datetime import datetime


class User(Document):
    name: str
    email: EmailStr
    created_at: datetime

    class Settings:
        name = "users"
