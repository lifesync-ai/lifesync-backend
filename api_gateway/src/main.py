# api_gateway/src/main.py
from fastapi import FastAPI, status
from datetime import datetime, timezone
from api_gateway.src.api.router import api_router

app = FastAPI(
    title="LifeSync AI - API Gateway",
    version="0.1.0",
    description="The secure entrypoint for the LifeSync AI ecosystem"
)

# Simple health check endpoint left in main for fast diagnostics
@app.get('/health', tags=["System"])
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc)}

# Include our modular API routes
app.include_router(api_router)
