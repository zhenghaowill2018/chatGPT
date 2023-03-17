import datetime
import json
import _asyncio
import asyncio

class Json_Encode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(datetime.datetime.timestamp(obj))
        elif isinstance(obj, (asyncio.Future, _asyncio.Future)):
            return str(obj)
        elif isinstance(obj, (type, TypeError, AttributeError)):
            return str(obj.args)
        else:
            return json.JSONEncoder.default(self, obj)
