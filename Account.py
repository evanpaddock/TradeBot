from schwab.auth import Client, easy_client
import os


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
