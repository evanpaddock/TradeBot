import os
from dotenv import load_dotenv
import account, notification, utils, order
from flask import (
    Flask,
    make_response,
    jsonify,
    request,
)

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
        new_order = order.Order(order_like=order_data, account=account)
        message = new_order.buy()
        resp = "Order successfully placed.", 200
    except:
        message = "There was an issue placing a buy order."
        resp = "There is an issue with the data being sent.", 400
    finally:
        # notification.send_sms_via_email(message)
        return resp


@app.route("/Order/Equity/Sell", methods=["POST"])
def sell_order():
    order_data = request.get_json()
    if order_data["type"] != "SELL":
        return "Invalid Sell Order", 400

    try:
        new_order = order.Order(order_like=order_data, account=account)
        input(new_order)
        message = new_order.sell()
        resp = "Order successfully placed.", 200
    except:
        message = "There was an issue placing a sell order."
        resp = "There is an issue with the data being sent.", 400
    finally:
        # notification.send_sms_via_email(message)
        return resp


@app.route("/Order/Equity/Get", methods=["POST"])
def get_orders():
    order_data = request.get_json()
    if order_data["type"] != "CANCEL":
        return "Invalid Cancel Order", 400

    try:
        order_data["status"]
    except:
        order_data["status"] = None

    try:
        orders = order.Order.get_all_orders(
            account.account_hash, account.client, order_data["status"]
        )

        resp = utils.json_rtp(orders), 200
    except:
        resp = "There is an issue with the data being sent.", 400
    finally:
        return resp


@app.route("/Order/Equity/Cancel", methods=["POST"])
def cancel_order():
    order_data = request.get_json()
    if order_data["type"] != "CANCEL":
        return "Invalid Cancel Order", 400

    try:
        new_order = order.Order(order_id=order_data["order_id"], account=account)
        new_order.get_order()
        message = new_order.cancel()
        resp = "Order successfully cancelled.", 200
    except:
        message = "There was an issue placing a cancel order."
        resp = "There is an issue with the data being sent.", 400
    finally:
        # notification.send_sms_via_email(message)
        return resp


@app.route("/shutdown", methods=["POST"])
def shutdown():
    KEY = request.get_json()["SHUTDOWN_KEY"]
    if KEY == os.getenv("SHUTDOWN_KEY"):
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
    account = account.Account()
    order.Order.cancel_all_open_orders(account.client, account.account_hash)
    # app.run(debug=True)
    print("Ending TradeBot...")
