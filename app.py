import sys
from dotenv import load_dotenv
import Order, Account, Notification, Utils
from flask import Flask, make_response, jsonify

app = Flask(__name__)

load_dotenv(".env")
client, account_hash = Account.setup()
# Notification.send_sms_via_email(f"App successfully running for client: {client.get_account_numbers().json()[0]["accountNumber"]}")


@app.route("/")
def index():
    return "<h1>Welcome to TradeBot!</h1>"


@app.route("/Market/Positions/Current")
def open_positions():
    return make_response("", 204)


@app.route("/Market/Time/Current")
def current_time():
    hours = Utils.get_market_hours(client)
    if len(hours) > 2:
        message = hours
    else:
        message = f"{hours[0]}-{hours[1]}"
    return jsonify(message)


@app.route("/shutdown", methods=["POST"])
def shutdown():

    return "Server shutting down...", 200


if __name__ == "__main__":
    app.run(debug=True)
    print("Ending TradeBot...")
