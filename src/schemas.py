from datetime import datetime
from typing    import List, Optional
from pydantic import BaseModel, Field

class Headline(BaseModel):
    title:        str
    url:          str
    source:       str
    published_at: datetime

class MarketData(BaseModel):
    cap:  float = Field(..., description="Market cap in USD")
    rank: int   = Field(..., description="Market cap rank")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer:      str
    price:       Optional[float]
    market_cap:  Optional[float]
    rank:        Optional[int]
    headlines:   Optional[List[str]]
