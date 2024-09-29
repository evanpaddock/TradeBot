import json
import httpx
from schwab.auth import Client


def json_rtp(json_object: str):
    json_data = json.dumps(json_object, indent=4)
    return json_data


def get_market_hours(client: Client):
    response = client.get_market_hours(Client.MarketHours.Market.EQUITY)
    assert response.status_code == httpx.codes.OK, response.raise_for_status()
    data = response.json()["equity"]["equity"]
    if data["isOpen"]:
        regular_market_hours = data["sessionHours"]["regularMarket"]["start"]
        market_open = regular_market_hours["start"].split("T")[1].split("-")[0]
        market_close = regular_market_hours["end"].split("T")[1].split("-")[0]
        return (market_open, market_close)
    else:
        return "Market Closed"
