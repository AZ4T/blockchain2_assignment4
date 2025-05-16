import feedparser
from datetime import datetime
from typing import List
from ..schemas import Headline

RSS_URL = "https://cointelegraph.com/tags/{symbol}/rss"

async def get_headlines(symbol: str) -> List[Headline]:
    url = RSS_URL.format(symbol=symbol.lower())
    feed = feedparser.parse(url)
    entries = feed.entries[:5]
    headlines = []
    for e in entries:
        headlines.append(Headline(
            title=e.title,
            url=e.link,
            source="Cointelegraph",
            published_at=datetime(*e.published_parsed[:6])
        ))
    return headlines