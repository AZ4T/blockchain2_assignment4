# src/main.py
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import logging

from .services.exchange_service import get_price_cg
from .services.market_service import get_market_data
from .services.news_service import get_headlines
from .ai_client import answer_query

app = FastAPI()

logger = logging.getLogger("uvicorn.error")

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    q = req.question.strip()
    symbol = q.replace("?", "").upper().split()[-1]
    try:
        # 1) fetch on‐chain price
        symbol = req.question.strip().upper()
        price = await get_price_cg(symbol)
        # 2) build a prompt for GPT-2
        prompt = (
            f"You are a crypto assistant.\n"
            f"The current price of {symbol} is ${price:.2f}.\n"
            f"User asked: {req.question}\n"
            f"Please answer concisely:"
        )
        # 3) generate with our local pipeline
        answer = await answer_query(prompt, max_new_tokens=100)
        return {"answer": answer}
    except Exception as e:
        # log the full stack-trace
        logger.exception("❌ error in /api/chat")
        # return the message to the client (first 300 chars)
        raise HTTPException(status_code=500, detail=str(e)[:300])


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
