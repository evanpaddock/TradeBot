from schwab.auth import Client
from schwab.orders.equities import (
    equity_buy_limit,
    equity_buy_market,
    equity_sell_limit,
    equity_sell_market,
)
from .Notification import send_sms_via_email
import json
import os


def write_transation(order_id: int, symbol: str, quantity: int):
    with open(os.getenv("ORDERS_PATH"), "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
    new_data = {"order_id": order_id, "symbol": symbol, "quantity": quantity}
    data.append(new_data)

    with open(os.getenv("ORDERS_PATH"), "w") as f:
        json.dump(data, f, indent=4)


def buy_order(
    client: Client, account_hash: str, symbol: str, quantity: int, price: float = None
):
    if price:
        order = equity_buy_limit(symbol, quantity, price)
    else:
        order = equity_buy_market(symbol, quantity)

    order_status = client.place_order(account_hash, order)
    input(order_status)
    if order_status:
        write_transation(order_status, symbol, quantity)
        message = f"Order to buy {quantity} share{'s' if quantity > 1 else ''} of {symbol} was successful."
    else:
        message = f"Order to buy {quantity} share{'s' if quantity > 1 else ''} of {symbol} has failed. Please check the application for a more specific error."

    send_sms_via_email(message)


def sell_order(
    client: Client, account_hash: str, symbol: str, quantity: int, price: float = None
):
    if price:
        order = equity_sell_limit(symbol, quantity, price)
    else:
        order = equity_sell_market(symbol, quantity)

    order_status = client.place_order(account_hash, order)

    if order_status:
        message = f"Order to sell {quantity} share{'s' if quantity > 1 else ''} of {symbol} was successful."
    else:
        message = f"Order to sell {quantity} share{'s' if quantity > 1 else ''} of {symbol} has failed. Please check the application for a more specific error."

    send_sms_via_email(message)


def cancel_order(
    client: Client,
    order_id: int,
    account_hash: str,
    symbol: str,
    quantity: float,
    remaining_quantity: float = 0.0,
    filled_quanitity: float = 0.0,
):
    Client.cancel_order(client, order_id, account_hash)
    if filled_quanitity > 0:
        message = f"Order {order_id} for {quantity} shares of {symbol} was cancelled, but {filled_quanitity} were filled and {remaining_quantity} were remianing."
    else:
        message = f"Order {order_id} for {quantity} shares of {symbol} was cancelled"

    send_sms_via_email(message)


def cancel_all_open_orders(client: Client, account_hash: str):
    open_orders = client.get_orders_for_account(
        account_hash, status=client.Order.Status.PENDING_ACTIVATION
    ).json()
    for open_order in open_orders:
        symbol = open_order["orderLegCollection"][0]["instrument"]["symbol"]
        quantity = open_order["quantity"]
        filled_quantity = open_order["filledQuantity"]
        remaining_quantity = open_order["remainingQuantity"]
        order_id = open_order["orderId"]
        cancel_order(
            client,
            order_id,
            account_hash,
            symbol,
            quantity,
            remaining_quantity,
            filled_quantity,
        )
