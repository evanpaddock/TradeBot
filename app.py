import os
from dotenv import load_dotenv
from schwab.auth import easy_client, Client

from models import Order


def setup():
    client = get_client()
    account_hash = get_account_hash(client)
    return (client, account_hash)


def get_account_hash(client: Client) -> any:
    accountHash = client.get_account_numbers().json()[0]["hashValue"]
    return accountHash


def get_client():
    api_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    callback_url = os.getenv("CALLBACK_URL")
    token_path = os.getenv("TOKEN_PATH")

    return easy_client(api_key, app_secret, callback_url, token_path)


if __name__ == "__main__":
    load_dotenv(".env")
    client, account_hash = setup()
    # Order.buy_order(client, account_hash, "F", 1)
    Order.cancel_all_open_orders(client, account_hash)
