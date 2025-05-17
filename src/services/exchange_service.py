# src/services/exchange_service.py
import httpx, asyncio

COINGECKO_BASE     = "https://api.coingecko.com/api/v3"
_symbol_id_map: dict[str, str] | None = None
_map_lock = asyncio.Lock()

async def _ensure_symbol_map() -> dict[str, str]:
    global _symbol_id_map
    if _symbol_id_map is None:
        async with _map_lock:
            if _symbol_id_map is None:
                url = f"{COINGECKO_BASE}/coins/list"
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.get(url)
                    r.raise_for_status()
                    coins = r.json()
                _symbol_id_map = {c["symbol"].upper(): c["id"] for c in coins}
    return _symbol_id_map

async def get_price_cg(symbol: str) -> float:
    mapping = await _ensure_symbol_map()
    sym     = symbol.upper()
    if sym not in mapping:
        raise ValueError(f"Symbol '{sym}' not found on CoinGecko")
    coin_id = mapping[sym]

    url    = f"{COINGECKO_BASE}/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    async with httpx.AsyncClient(timeout=5.0) as client:
        r    = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    # <-- THIS IS A real float, e.g. 103249.00, not zero!
    return data[coin_id]["usd"]
