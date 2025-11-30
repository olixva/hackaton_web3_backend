from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"

    # Encryption Secret (must be a valid Fernet key)
    ENCRYPTION_SECRET: str = "your-default-fernet-key-here"

    # Destination address for payments
    DESTINATION_BSV_ADDRESS: str = "your-default-bsv-address-here"

    # Load environment variables from a .env file
    model_config = SettingsConfigDict(env_file=".env")


# Load settings and cache them
@lru_cache
def get_settings() -> Settings:
    return Settings()


# Easy access to the setting
settings = get_settings()