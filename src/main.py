# src/main.py
import re
import logging
import asyncio
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .schemas import ChatRequest, ChatResponse
from .services.exchange_service import get_price_cg
from .services.market_service   import get_market_data
from .services.news_service     import get_headlines
from .ai_client import answer_query

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

class ChatRequest(BaseModel):
    question: str

_STOP = {"WHAT","IS","THE","PRICE","OF","TELL","ME","ABOUT","LATEST","NEWS","AND"}

def extract_symbol(text: str) -> Optional[str]:
    tokens   = re.findall(r"\b[A-Za-z]{2,5}\b", text)
    filtered = [t for t in tokens if t.upper() not in _STOP]
    return filtered[-1].upper() if filtered else None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    question = req.question.strip()
    symbol   = extract_symbol(question)

    price, mkt, news = None, None, None
    if symbol:
        try:
            price_coro  = get_price_cg(symbol)
            market_coro = get_market_data(symbol)
            news_coro   = get_headlines(symbol)
            price, mkt, news = await asyncio.gather(
                price_coro, market_coro, news_coro
            )
        except Exception as e:
            logger.error(f"Fetch failed for {symbol}: {e}")
            raise HTTPException(404, detail=f"Could not fetch data for '{symbol}'")

    # 2) Only if we got all three, build prompt context
    context: List[str] = []
    if symbol and price is not None and mkt and news:
        context = [
            f"Here’s the latest on {symbol}:",
            f"- Price: ${price:,.2f}",                 # <-- real price now
            f"- Market cap: ${mkt.cap:,.0f}",
            f"- Rank: #{mkt.rank}",
            "- Top headlines:"
        ] + [
            f"  {i+1}. {h.title} ({h.source})"
            for i,h in enumerate(news)
        ]

    prompt = (
        ("\n".join(context) + "\n\n") if context else ""
    ) + f"User asked: “{question}”\nAnswer concisely based on the data above."

    try:
        ai_text = await answer_query(prompt)
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(500, detail="Internal LLM error")

    return ChatResponse(
        answer     = ai_text.strip(),
        price      = price,
        market_cap = mkt.cap  if mkt else None,
        rank       = mkt.rank if mkt else None,
        headlines  = [h.title for h in news] if news else None,
    )


class TokenResponse(BaseModel):
    symbol: str
    price: float

@app.get("/api/token/{symbol}", response_model=TokenResponse)
async def token(symbol: str):
    try:
        price = await get_price_cg(symbol)
        return {"symbol": symbol.upper(), "price": price}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/market/{symbol}")
async def market(symbol: str):
    try:
        return await get_market_data(symbol)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/news/{symbol}")
async def news(symbol: str):
    try:
        return await get_headlines(symbol)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# static files
BASE_DIR = Path(__file__).parent.parent
static_dir = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_spa():
    return FileResponse(static_dir / "index.html")
