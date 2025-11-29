from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://hackaton-web3-frontend.vercel.app"
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
)

app.include_router(user_router)
app.include_router(meter_router)