from redis import Redis
from scrapy.utils.serialize import ScrapyJSONEncoder
from twisted.internet.threads import deferToThread

from .models import EventItem

redis_conn = Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

default_serialize = ScrapyJSONEncoder().encode
events_list_key = 'events:list'
event_key = 'events:{match_id}'


class RedisPipeline(object):
    """Pushes serialized item into a redis list/queue

    Settings
    --------
    REDIS_ITEMS_KEY : str
        Redis key where to store items.
    REDIS_ITEMS_SERIALIZER : str
        Object path to serializer function.

    """

    def __init__(self,
                 serialize_func=default_serialize):
        """Initialize pipeline.

        Parameters
        ----------
        serialize_func : callable
            Items serializer function.

        """
        self.server = redis_conn
        self.serialize = serialize_func

    def process_item(self, item: EventItem, spider):
        return deferToThread(self._process_item, item, spider)

    def _process_item(self, item: EventItem, spider):
        key = event_key.format(match_id=item.id)
        data = self.serialize(item)
        self.server.set(key, data)
        self.server.lpush(events_list_key, item.id)
        return item
