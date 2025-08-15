import re

def is_valid_symbol(symbol: str) -> bool:
    return re.match(r'^[A-Z]+:[A-Z0-9\.\-]+$', symbol.upper()) is not None

# Supported intervals from TradingView (adjust if needed)
VALID_INTERVALS = {
    "1s", "5s", "15s",
    "1m", "3m", "5m", "15m", "30m",
    "1h", "2h", "4h", "1D", "1W", "1M"
}

def is_valid_interval(interval: str) -> bool:
    return interval in VALID_INTERVALS
