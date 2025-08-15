# app/services/websocket_client.py

import asyncio
import json
import random
import websockets
import re

WS_URL = "wss://data.tradingview.com/socket.io/websocket"

def generate_session(prefix: str) -> str:
    return f"{prefix}_{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=12))}"

def format_message(function: str, *args) -> str:
    data = json.dumps({
        "m": function,
        "p": list(args)
    })
    return f"~m~{len(data)}~m~{data}"

async def fetch_data_with_ws(symbol: str, interval: str = "1m"):
    session = generate_session("qs")  # Chart session

    async with websockets.connect(WS_URL, origin="https://www.tradingview.com") as ws:
        await ws.send(format_message("set_auth_token", ""))  # Anonymous user

        await ws.send(format_message("chart_create_session", session, ""))
        await ws.send(format_message("quote_create_session", session))
        await ws.send(format_message("quote_add_symbols", session, symbol))

        # Optional: send interval request for candles (not just quote)
        await ws.send(format_message("resolve_symbol", session, symbol))
        await ws.send(format_message("create_series", session, "s1", "s1", symbol, interval, 300))

        price = None

        for _ in range(20):  # Read 20 messages max
            response = await ws.recv()

            matches = re.findall(r'~m~\d+~m~({.*?})', response)
            for match in matches:
                msg = json.loads(match)
                if msg.get("m") == "qsd":
                    for d in msg["p"][1]["v"]:
                        if d.get("s") == symbol and "lp" in d:
                            price = d["lp"]
                            return {
                                "price": price,
                                "symbol": symbol,
                                "source": "websocket"
                            }

        raise RuntimeError("Price not found in WebSocket messages.")
