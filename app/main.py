from fastapi import FastAPI
from app.api.v1 import endpoints
from app.core.logger import setup_logger

app = FastAPI(title="Custom TradingView API")

setup_logger()
app.include_router(endpoints.router, prefix="/api/v1")
