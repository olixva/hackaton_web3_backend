from fastapi import FastAPI
from contextlib import asynccontextmanager

# Routers
from app.routes.user_route import user_router
from app.routes.meter_route import meter_router

# Database
from app.config.mongo import MongoDbClient

mongo_client = MongoDbClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("Starting up...")
    await mongo_client.init()
    yield
    # Shutdown actions
    await mongo_client.close()
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
app.include_router(meter_router)