import os
from dotenv import load_dotenv
from schwab.auth import *
from schwab.orders import *
from schwab.streaming import *
import asyncio


async def main():
    client = get_client()
    data = await get_account(client)
    account_hash = data.json()[0]["hashValue"]
    stream_client = StreamClient(client, account_id=account_hash)
    await read_stream(stream_client)


async def get_account(client):
    data = await client.get_account_numbers()
    return data


def get_client():
    api_key = os.getenv("APP_KEY")
    app_secret = os.getenv("APP_SECRET")
    callback_url = os.getenv("CALLBACK_URL")
    token_path = os.getenv("TOKEN_PATH")

    return easy_client(api_key, app_secret, callback_url, token_path, asyncio=True)


async def read_stream(stream_client):
    await stream_client.login()

    def print_message(message):
        print(json.dumps(message, indent=4))

    # Always add handlers before subscribing because many streams start sending
    # data immediately after success, and messages with no handlers are dropped.
    stream_client.add_nasdaq_book_handler(print_message)
    await stream_client.nasdaq_book_subs(["SPY"])

    while True:
        await stream_client.handle_message()


if __name__ == "__main__":
    load_dotenv(".env")
    asyncio.run(main())
