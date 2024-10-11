import os
from dotenv import load_dotenv
from account import Account
from notification import Notification
from order_types import Equity
from flask import (
    Flask,
    make_response,
    jsonify,
    request,
)

import utils

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return "<h1>Welcome to TradeBot!</h1>"


@app.route("/Order/Equity/Buy", methods=["POST"])
def buy_order():
    order_data = request.get_json()
    if order_data["type"] != "BUY":
        return "Invalid Buy Order", 400
    try:
        new_order = Equity(
            account=account, order_like=order_data, notification=notification
        )
        message = new_order.buy()
        resp = "Order successfully placed.", 200
    except Exception as e:
        message = f"Failed to buy an order. Error: {e}"
        resp = f"There is an issue with the data being sent. Error: {e}", 400
    finally:
        if notification and message:
            notification.send_sms_via_email(message)
        return resp


@app.route("/Order/Equity/Sell", methods=["POST"])
def sell_order():
    order_data = request.get_json()
    if order_data["type"] != "SELL":
        return "Invalid Sell Order", 400

    try:
        new_order = Equity(
            order_like=order_data, account=account, notification=notification
        )
        input(new_order)
        message = new_order.sell()
        resp = "Order successfully placed.", 200
    except Exception as e:
        message = f"Failed to place a sell order. Error: {e}"
        resp = f"There is an issue with the data being sent. Error: {e}", 400
    finally:
        if notification and message:
            notification.send_sms_via_email(message)
        return resp


@app.route("/Order/Equity/Get", methods=["POST"])
def get_orders():
    order_data = request.get_json()
    if order_data["type"] != "Get":
        return "Invalid Get Order", 400

    try:
        order_status = order_data["status"]
    except:
        order_status = None

    try:
        if order_status:
            order_status = Equity.status_dict[order_data["status"]]

        orders = Equity.get_all_orders(
            account.account_hash, account.client, order_status
        )

        resp = utils.json_rtp(orders), 200
    except Exception as e:
        resp = f"Failed to buy an order. Error: {e}", 400
    finally:
        return resp


@app.route("/Order/Equity/Cancel", methods=["POST"])
def cancel_order():
    order_data = request.get_json()
    if order_data["type"] != "CANCEL":
        return "Invalid Cancel Order", 400

    try:
        new_order = Equity(
            order_id=order_data["order_id"], account=account, notification=notification
        )
        new_order.get_order()
        message = new_order.cancel()
        resp = "Order successfully cancelled.", 200
    except Exception as e:
        message = f"There was an issue placing a cancel order. Error: {e}"
        resp = f"There is an issue with the data being sent. Error: {e}", 400
    finally:
        if notification and message:
            notification.send_sms_via_email(message)
        return resp


@app.route("/shutdown", methods=["POST"])
def shutdown():
    KEY = request.get_json()["SHUTDOWN_KEY"]
    if KEY == os.getenv("SHUTDOWN_KEY"):
        print("Ending TradeBot...")

        if notification:
            notification.send_sms_via_email("Ending TradeBot...")

        shutdown_func = request.environ.get("werkzeug.server.shutdown")

        if shutdown_func is None:
            # If not running on Werkzeug, fallback to exit the process
            os._exit(0)  # This forces the app to exit

        shutdown_func()
    else:
        return "Invalid Key", 403


if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv(".env")

    # Setup client and account_hash by calling the account setup function
    account = Account()

    # notification = Notification()
    notification = None

    app.run(debug=True)
