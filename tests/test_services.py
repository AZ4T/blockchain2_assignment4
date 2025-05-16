import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.services.exchange_service import get_price
from src.services.market_service import get_market_data
from src.services.news_service import get_headlines
from src.ai_client import summarize_token

async def test_all():
    sym='ETH'
    print('Price:', await get_price(sym))
    print('Market:', await get_market_data(sym))
    print('Headlines count:', len(await get_headlines(sym)))
    summary=await summarize_token({'symbol':sym,'price':await get_price(sym),'market_cap':(await get_market_data(sym)).cap,'rank':(await get_market_data(sym)).rank,'headlines':await get_headlines(sym)})
    print('Summary:', summary)

if __name__=='__main__': asyncio.run(test_all())