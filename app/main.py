from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Import routers for different endpoints
from app.routes.user_route import user_router
from app.routes.meter_route import meter_router
from app.routes.alarm_route import alarm_router

# Import database client
from app.config.mongo import MongoDbClient

# Initialize MongoDB client
mongo_client = MongoDbClient()

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print("Starting up...")
    await mongo_client.init()
    yield
    # Shutdown actions
    await mongo_client.close()
    print("Shutting down...")

# Create FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hackaton-web3-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
)

# Include routers for user, meter, and alarm endpoints
app.include_router(user_router)
app.include_router(meter_router)
app.include_router(alarm_router)