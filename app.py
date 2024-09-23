from dotenv import load_dotenv
import os
from schwab.auth import client_from_login_flow
from schwab.orders.equities import equity_buy_market

if __name__ == "__main__":
    load_dotenv()
    
    client = client_from_login_flow(
        os.getenv("APP_KEY"),
        os.getenv("APP_SECRET"),
        os.getenv("CALLBACK_URL"),
        "./token.json",
    )
