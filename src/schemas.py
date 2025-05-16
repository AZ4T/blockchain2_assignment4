from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class Headline(BaseModel):
    title: str
    url: str
    source: str
    published_at: datetime

class MarketData(BaseModel):
    cap: float = Field(..., description="Market cap in USD")
    rank: int = Field(..., description="Market cap rank")

class TokenSummaryResponse(BaseModel):
    symbol: str
    price: float
    market_data: MarketData
    headlines: List[Headline]
    summary: str