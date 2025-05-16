import httpx
# example alternative
async def get_price_cg(symbol: str) -> float:
    url = "https://api.coingecko.com/api/v3/simple/price"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={
            "ids": symbol.lower(),
            "vs_currencies": "usd",
        })
        r.raise_for_status()
        data = r.json()
    return data[symbol.lower()]["usd"]
