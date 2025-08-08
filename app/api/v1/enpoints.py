from fastapi import APIRouter, Query
from app.services.data_router import get_price_data

router = APIRouter()

@router.get("/price")
async def get_price(symbol: str = Query(...), interval: str = Query("1m")):
    result = await get_price_data(symbol, interval)
    return {"symbol": symbol, "interval": interval, "data": result}
