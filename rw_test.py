import asyncio
from app.services.websocket_client import fetch_data_with_ws

if __name__ == "__main__":
    symbol = "NASDAQ:AAPL"
    data = asyncio.run(fetch_data_with_ws(symbol))
    print(data)
