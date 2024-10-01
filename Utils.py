import json
import httpx
from schwab.auth import Client
from datetime import datetime, timedelta


def json_rtp(json_object: str):
    json_data = json.dumps(json_object, indent=4)
    return json_data


def get_market_hours(client: Client):
    response = client.get_market_hours(Client.MarketHours.Market.EQUITY)
    assert response.status_code == httpx.codes.OK, response.raise_for_status()
    data = response.json()["equity"]["EQ"]
    if data["isOpen"]:
        regular_market_hours = data["sessionHours"]["regularMarket"][0]["start"]
        cst_time = est_to_cst(regular_market_hours)
        market_open = cst_time.split("T")[1].split("-")[0][0:-3]
        market_close = cst_time.split("T")[1].split("-")[1]
        return (market_open, market_close)
    else:
        return "Market Closed"


def est_to_cst(est_time_str):
    """Converts an EST time string to CST."""

    try:
        # Try parsing a full ISO format string first
        est_time = datetime.fromisoformat(est_time_str)
    except ValueError:
        # If the string is not a full ISO format, handle just the time part
        today = datetime.today().date()  # Use today's date
        est_time = datetime.combine(
            today, datetime.strptime(est_time_str, "%H:%M").time()
        )

    # Convert to CST (which is 1 hour behind EST)
    cst_time = est_time - timedelta(hours=1)

    # Format the CST time as a string
    cst_time_str = cst_time.isoformat()

    return cst_time_str
