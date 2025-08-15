from fastapi import APIRouter, Query, HTTPException
from app.services.data_router import get_price_data
from app.utils.validation import is_valid_symbol, is_valid_interval

router = APIRouter()

@router.get("/price")
async def get_price(symbol: str = Query(...), interval: str = Query("1m")):
    if not is_valid_symbol(symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")

    if not is_valid_interval(interval):
        raise HTTPException(status_code=400, detail=f"Invalid interval. Supported: {', '.join(sorted(is_valid_interval.VALID_INTERVALS))}")

    result = await get_price_data(symbol, interval)
    return {"symbol": symbol, "interval": interval, "data": result}

@router.get("/health")
async def health_check():
    return {"status": "ok"}
