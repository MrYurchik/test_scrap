import json
import scrapy

from ..models import OutcomeItem, MarketItem, EventItem


class UA1xbetSpider(scrapy.Spider):
    name = 'ua1xbet'
    allowed_domains = ['ua1xbet.com']
    start_urls = [
        'https://ua1xbet.com/LiveFeed/Get1x2_VZip?sports=1&count=50&lng=en&mode=4&country=2&partner=25&getEmpty=true&noFilterBlockEvent=true']

    def parse(self, response: scrapy.http.HtmlResponse):
        js = json.loads(response.text)['Value']
        ids = [id['I'] for id in js]
        for match_id in ids:
            yield self.request_match(match_id)

    def request_match(self, match_id: str) -> scrapy.Request:
        url = f'https://ua1xbet.com/LiveFeed/GetGameZip?id={match_id}&lng=en&cfview=0&isSubGames=true&GroupEvents=true&allEventsGroupSubGames=true&countevents=250&partner=25&marketType=1&isNewBuilder=true'
        req = scrapy.Request(url, callback=self.parse_match)
        return req

    def parse_match(self, response: scrapy.http.HtmlResponse):
        js = json.loads(response.text)['Value']
        home = js['O1']
        away = js['O2']
        # pdb.set_trace()
        s1 = js['SC']['FS'].get('S1', 0)
        s2 = js['SC']['FS'].get('S2', 0)
        score = f'{s1}:{s2}'
        outcome_1, outcome_x, outcome_2, outcome_yes, outcome_no = None, None, None, None, None
        for el in js['GE']:
            if el['G'] == 1:
                outcome_1 = OutcomeItem(active=not bool(el['E'][0][0].get('B')), odd=el['E'][0][0]['C'], type='1')
                outcome_x = OutcomeItem(active=not bool(el['E'][1][0].get('B')), odd=el['E'][1][0]['C'], type='X')
                outcome_2 = OutcomeItem(active=not bool(el['E'][2][0].get('B')), odd=el['E'][2][0]['C'], type='2')
            elif el['G'] == 19:
                outcome_yes = OutcomeItem(active=not bool(el['E'][0][0].get('B')), odd=el['E'][0][0]['C'], type='Yes')
                outcome_no = OutcomeItem(active=not bool(el['E'][1][0].get('B')), odd=el['E'][1][0]['C'], type='No')
        markets = []
        if all((outcome_1, outcome_x, outcome_2)):
            market_regular = MarketItem(title='1X2 Regular time', outcomes=[outcome_1, outcome_x, outcome_2])
            markets.append(market_regular)
        if all((outcome_yes, outcome_no)):
            market_both = MarketItem(title='Both Teams To Score', outcomes=[outcome_yes, outcome_no])
            markets.append(market_both)

        event = EventItem(id=js['I'], away=away, home=home, currentScore=score, markets=markets)
        yield event
