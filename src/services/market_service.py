import httpx
from typing import List
from ..schemas import MarketData
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

async def get_market_data(symbol: str) -> MarketData:
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 50, "page": 1}
    async with httpx.AsyncClient() as client:
        r = await client.get(COINGECKO_URL, params=params)
        r.raise_for_status()
        data: List[dict] = r.json()
    for c in data:
        if c["symbol"].lower() == symbol.lower():
            return MarketData(cap=c["market_cap"], rank=c["market_cap_rank"])
    raise ValueError(f"Symbol '{symbol}' not found in top 50.")