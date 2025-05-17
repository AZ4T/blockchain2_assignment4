import feedparser
from datetime import datetime
from typing import List

from ..schemas import Headline
from .exchange_service import _ensure_symbol_map

RSS_URL_TEMPLATE = "https://cointelegraph.com/tags/{coin_id}/rss"

async def get_headlines(symbol: str, limit: int = 5) -> List[Headline]:
    """
    Fetch the top `limit` headlines for the given ticker
    by mapping "ETH"→"ethereum" and hitting its RSS feed.
    """
    # 1) Map ticker → full coin ID
    mapping = await _ensure_symbol_map()
    sym = symbol.upper()
    if sym not in mapping:
        raise ValueError(f"Symbol '{sym}' not found for headlines")

    coin_id = mapping[sym]

    # 2) Parse the RSS feed for that coin
    url = RSS_URL_TEMPLATE.format(coin_id=coin_id)
    feed = feedparser.parse(url)
    entries = feed.entries[:limit]

    # 3) Build and return Headline models
    headlines: List[Headline] = []
    for e in entries:
        # published_parsed is a time.struct_time
        published = datetime(*e.published_parsed[:6])
        headlines.append(Headline(
            title        = e.title,
            url          = e.link,
            source       = "Cointelegraph",
            published_at = published
        ))
    return headlines
