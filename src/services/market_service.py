# src/services/market_service.py
import httpx
from typing    import List
from ..schemas import MarketData

COINGECKO_MARKETS = "https://api.coingecko.com/api/v3/coins/markets"

async def get_market_data(symbol: str) -> MarketData:
    params = {
        "vs_currency": "usd",
        "order":       "market_cap_desc",
        "per_page":    50,
        "page":        1
    }
    async with httpx.AsyncClient(timeout=5.0) as client:
        r    = await client.get(COINGECKO_MARKETS, params=params)
        r.raise_for_status()
        data: List[dict] = r.json()

    for coin in data:
        if coin["symbol"].lower() == symbol.lower():
            return MarketData(
                cap  = coin["market_cap"],
                rank = coin["market_cap_rank"]
            )
    raise ValueError(f"Symbol '{symbol}' not in top 50.")
