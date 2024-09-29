from schwab.auth import Client
from schwab.orders.equities import (
    equity_buy_limit,
    equity_buy_market,
    equity_sell_limit,
    equity_sell_market,
)
import Notification


def buy_order(
    client: Client, account_hash: str, symbol: str, quantity: int, price: float = None
):
    if price:
        order = equity_buy_limit(symbol, quantity, price)
    else:
        order = equity_buy_market(symbol, quantity)

    order_response = client.place_order(account_hash, order)

    if order_response:
        message = f"Order to buy {quantity} share{'s' if quantity > 1 else ''} of {symbol}{f' at {price}' if price != None else ''} was sent successful."
    else:
        message = f"Order to buy {quantity} share{'s' if quantity > 1 else ''} of {symbol} has failed. Please check the application for a more specific error."

    Notification.send_sms_via_email(message)


def sell_order(
    client: Client, account_hash: str, symbol: str, quantity: int, price: float = None
):
    if price:
        order = equity_sell_limit(symbol, quantity, price)
    else:
        order = equity_sell_market(symbol, quantity)

    order_response = client.place_order(account_hash, order)

    if order_response:
        message = f"Order to sell {quantity} share{'s' if quantity > 1 else ''} of {symbol} was sent successful."
    else:
        message = f"Order to sell {quantity} share{'s' if quantity > 1 else ''} of {symbol} has failed. Please check the application for a more specific error."

    Notification.send_sms_via_email(message)


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

    return message


def get_all_orders(
    account_hash: str, client: Client, status: Client.Order.Status = None
):
    return client.get_orders_for_account(account_hash, status=status).json()


def cancel_all_open_orders(client: Client, account_hash: str):
    open_orders = get_all_orders(
        account_hash, client, client.Order.Status.PENDING_ACTIVATION
    )
    messages = []
    if len(open_orders) == 0:
        messages.append(f"No open orders to be closed.")
    else:
        for open_order in open_orders:
            symbol = open_order["orderLegCollection"][0]["instrument"]["symbol"]
            quantity = open_order["quantity"]
            filled_quantity = open_order["filledQuantity"]
            remaining_quantity = open_order["remainingQuantity"]
            order_id = open_order["orderId"]
            message = cancel_order(
                client,
                order_id,
                account_hash,
                symbol,
                quantity,
                remaining_quantity,
                filled_quantity,
            )
            messages.append(message + "<br><br>")
    print(messages)
    Notification.send_sms_via_email(messages)
