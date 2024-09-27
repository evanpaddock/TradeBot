import os
from dotenv import load_dotenv
from schwab.auth import easy_client, Client
from models import Order, Account, Notification
from flask import Flask, make_response

app = Flask(__name__)

load_dotenv(".env")
client, account_hash = Account.setup()
Notification.send_sms_via_email(f"App successfully running for client: {client.get_account_numbers().json()[0]["accountNumber"]}")

@app.route("/")
def hello_world():
    return make_response('', 204)


if __name__ == "__main__":
    app.run(port=5000)
    print("Ending TradeBot...")
