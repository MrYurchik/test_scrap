import json

from flask import Flask, request
from redis import Redis

from xbet.xbet.redis_pipeline import event_key, events_list_key

redis_conn = Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)
app = Flask(__name__)


def return_events(start, end):
    events = redis_conn.lrange(events_list_key, start, end)
    result = []
    for match_id in events:
        event_str = redis_conn.get(event_key.format(match_id=match_id))
        event = json.loads(event_str)
        result.append(event)
    return result


@app.route("/events")
def events():
    start = int(request.args.get("start", 0))
    end = int(request.args.get("end", 10))
    return return_events(start, end)


if __name__ == "__main__":
    app.run()
