import json
import httpx
from schwab.auth import Client
from datetime import datetime, timedelta


def json_rtp(json_object: str):
    json_data = json.dumps(json_object, indent=4)
    return json_data
