import asyncio
import logging

import aiohttp

from xbet.xbet.models import EventItem, MarketItem, OutcomeItem
from xbet.xbet.redis_pipeline import RedisPipeline

logging.basicConfig(level=logging.INFO)
start_url = "https://ua1xbet.com/LiveFeed/Get1x2_VZip?sports=1&count=50&lng=en&mode=4&country=2&partner=25&getEmpty=true&noFilterBlockEvent=true"
redis_pipeline = RedisPipeline()


async def save_product(match_info):
    redis_pipeline._process_item(match_info, None)
    logging.info(f"Item with id: {match_info.dict()['id']} saved to database...")


async def first_page(url):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, ssl=False) as response:
            js = dict(await response.json())["Value"]
            match_id_ids = [match_id["I"] for match_id in js]
            logging.info("First page with match ids parsed...")
            return match_id_ids


async def parse_match(js):
    js = js["Value"]
    home = js["O1"]
    away = js["O2"]
    s_1 = js["SC"]["FS"].get("S1", 0)
    s_2 = js["SC"]["FS"].get("S2", 0)
    score = f"{s_1}:{s_2}"
    outcome_1, outcome_x, outcome_2, outcome_yes, outcome_no = None, None, None, None, None
    for el in js["GE"]:
        if el["G"] == 1:
            if len(el["E"]) < 3:
                continue
            outcome_1 = OutcomeItem(active=not bool(el["E"][0][0].get("B")), odd=el["E"][0][0]["C"], type="1")
            outcome_x = OutcomeItem(active=not bool(el["E"][1][0].get("B")), odd=el["E"][1][0]["C"], type="X")
            outcome_2 = OutcomeItem(active=not bool(el["E"][2][0].get("B")), odd=el["E"][2][0]["C"], type="2")
        elif el["G"] == 19:
            outcome_yes = OutcomeItem(active=not bool(el["E"][0][0].get("B")), odd=el["E"][0][0]["C"], type="Yes")
            outcome_no = OutcomeItem(active=not bool(el["E"][1][0].get("B")), odd=el["E"][1][0]["C"], type="No")
    markets = []
    if all((outcome_1, outcome_x, outcome_2)):
        market_regular = MarketItem(title="1X2 Regular time", outcomes=[outcome_1, outcome_x, outcome_2])
        markets.append(market_regular)
    if all((outcome_yes, outcome_no)):
        market_both = MarketItem(title="Both Teams To Score", outcomes=[outcome_yes, outcome_no])
        markets.append(market_both)

    event = EventItem(id=js["I"], away=away, home=home, currentScore=score, markets=markets)
    logging.info(f"Item with id: {js['I']} parsed...")
    await save_product(event)


async def request_match(match_id: str):
    url = f"https://ua1xbet.com/LiveFeed/GetGameZip?id={match_id}&lng=en&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=250&partner=25&marketType=1&isNewBuilder=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            logging.info(f"Match with id {match_id} responsed...")
            await parse_match(await response.json())


async def main():
    match_ids = await first_page(start_url)
    tasks = []
    for match_id in match_ids:
        task = asyncio.create_task(request_match(match_id))
        tasks.append(task)
    logging.info("Task queue has been created, starting tasks...")
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
