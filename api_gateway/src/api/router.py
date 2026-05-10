# api_gateway/src/api/router.py
from fastapi import APIRouter
from api_gateway.src.api.v1.endpoints.planner import router as planner_router

# Base API Router for all endpoints
api_router = APIRouter()

# Include version 1 routers
# In the future, you can easily add api_router.include_router(users_router, prefix="/v1/users")
api_router.include_router(planner_router, prefix="/api/v1", tags=["Planner"])
