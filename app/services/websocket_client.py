# app/services/websocket_client.py

import asyncio
import json
import random
import re
import logging
import websockets
from typing import Optional

WS_URL = "wss://data.tradingview.com/socket.io/websocket"
MAX_ATTEMPTS = 3
MESSAGE_LIMIT = 20

logger = logging.getLogger(__name__)

def generate_session(prefix: str) -> str:
    return f"{prefix}_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=12))}"

def format_message(function: str, *args) -> str:
    data = json.dumps({
        "m": function,
        "p": list(args)
    })
    return f"~m~{len(data)}~m~{data}"

async def _connect_and_fetch(symbol: str, interval: str) -> Optional[float]:
    session = generate_session("qs")

    async with websockets.connect(WS_URL, origin="https://www.tradingview.com") as ws:
        await ws.send(format_message("set_auth_token", ""))
        await ws.send(format_message("chart_create_session", session, ""))
        await ws.send(format_message("quote_create_session", session))
        await ws.send(format_message("quote_add_symbols", session, symbol))
        
        # Optional: send interval request for candles (not just quote)
        await ws.send(format_message("resolve_symbol", session, symbol))
        await ws.send(format_message("create_series", session, "s1", "s1", symbol, interval, 300))

        price = None

        for _ in range(MESSAGE_LIMIT):
            response = await ws.recv()
            matches = re.findall(r'~m~\d+~m~({.*?})', response)
            for match in matches:
                try:
                    msg = json.loads(match)
                    if msg.get("m") == "qsd":
                        for d in msg["p"][1]["v"]:
                            if d.get("s") == symbol and "lp" in d:
                                price = d["lp"]
                                return price
                except Exception as e:
                    logger.warning(f"[WS Parse] Error decoding message: {e}")

    return None

async def fetch_data_with_ws(symbol: str, interval: str = "1m") -> dict:
    """
    Attempts to fetch live price data from TradingView WebSocket.
    """
    logger.info(f"[WS] Fetching live price for {symbol}...")

    attempt = 1
    while attempt <= MAX_ATTEMPTS:
        try:
            price = await _connect_and_fetch(symbol, interval)
            if price is not None:
                logger.info(f"[WS] Success: {symbol} -> {price}")
                return {
                    "price": price,
                    "symbol": symbol,
                    "interval": interval,
                    "source": "websocket"
                }
            else:
                raise RuntimeError("No price received from TradingView.")
        except Exception as e:
            logger.error(f"[WS Attempt {attempt}] Error: {e}")
            await asyncio.sleep(2 * attempt)
            attempt += 1

    raise RuntimeError(f"[WS] Failed to fetch price for {symbol} after {MAX_ATTEMPTS} attempts.")
