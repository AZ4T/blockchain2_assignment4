# src/main.py
import re
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .services.exchange_service import get_price_cg
from .services.market_service   import get_market_data
from .services.news_service     import get_headlines
from .ai_client import answer_query

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
async def chat(req: ChatRequest):
    q = req.question.strip()
    price = None
    symbol = None

    # 1) detect “price of XXX” queries and extract the ticker
    m = re.search(r"price of\s+([A-Za-z]+)", q, re.IGNORECASE)
    if m:
        symbol = m.group(1).upper()
        try:
            price = await get_price_cg(symbol)
        except Exception as e:
            logger.error(f"Price lookup failed for {symbol}: {e}")
            raise HTTPException(404, detail=f"Could not find price for symbol '{symbol}'")

    # 2) build a prompt for the LLM
    if price is not None:
        prompt = f"The current price of {symbol} is ${price:.2f} USD. {q}"
    else:
        prompt = q

    # 3) hand off to your local GPT‐2 pipeline (or any other model)
    try:
        raw = await answer_query(prompt)
        # unwrap if it's an OpenAI‐style dict or HF dict
        if isinstance(raw, dict):
            # OpenAI ChatCompletion → { choices: [ { message: { content } } ] }
            if "choices" in raw:
                choice = raw["choices"][0]
                # either GPT‐2 style: .text, or ChatCompletion: .message.content
                text = choice.get("text") or choice.get("message", {}).get("content", "")
            # HuggingFace inference → [ { generated_text: "…" } ]
            elif isinstance(raw, list) and raw and "generated_text" in raw[0]:
                text = raw[0]["generated_text"]
            else:
                # fallback
                text = str(raw)
        else:
            text = str(raw)
        return {"answer": text.strip()}
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail="Internal LLM error")


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
