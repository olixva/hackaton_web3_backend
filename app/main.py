from fastapi import FastAPI

# Routers
from app.routes.user_route import user_router

app = FastAPI()

app.include_router(user_router)