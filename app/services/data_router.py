# app/services/data_router.py

from app.utils.cache import get_cached_data, set_cached_data
from app.services.websocket_client import fetch_data_with_ws
from app.services.playwright_client import fetch_data_with_playwright

async def get_price_data(symbol: str, interval: str):
    # Try Redis cache first
    cached = await get_cached_data(symbol, interval)
    if cached:
        return cached

    # Try WebSocket first for low-latency data
    try:
        data = await fetch_data_with_ws(symbol, interval)
    except Exception as ws_err:
        print(f"[WS Fallback] WebSocket failed: {ws_err}")
        try:
            data = await fetch_data_with_playwright(symbol, interval)
        except Exception as browser_err:
            raise RuntimeError(f"All data sources failed: {browser_err}")

    # Store result in cache
    await set_cached_data(symbol, interval, data)
    return data
