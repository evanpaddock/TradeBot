import httpx
from schwab.auth import Client
from schwab.orders.equities import (
    equity_buy_limit,
    equity_buy_market,
    equity_sell_limit,
    equity_sell_market,
)
import Notification


class Order:
    """
    A class representing an order.

    Attributes:
        client (schwab.auth.Client): The client account.
        account_hash? (int): The hashed ID value of the account.
        symbol? (str): The symbol of the share.
        quantity? (int): The quantity of shares.
        price? (float): The limit price of the order.
        order_id? (int): The ID of the order.
        status? (Client.Order.Status): The status of the order.
    """

    def __init__(
        self,
        client: Client,
        account_hash: str = None,
        symbol: str = None,
        quantity: int = 0,
        price: float = None,
        order_id: int = None,
        status: Client.Order.Status = None,
    ):
        """
        Initializes an Order object.

        Parameters:
            client (schwab.auth.Client): The client account.
            account_hash? (int): The hashed ID value of the account.
            symbol? (str): The symbol of the share.
            quantity? (int): The quantity of shares.
            price? (float): The limit price of the order.
            order_id? (int): The ID of the order.
            status? (Client.Order.Status): The status of the order.
        """
        self.client = client
        self.account_hash = account_hash
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.status = status

    def __str__(self):
        """
        Print Current Order Details
        """
        message = ""

        for field, value in vars(self).items():
            message += f"{field}: {value}"

        return message

    def buy(self):
        if self.price:
            order = equity_buy_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_buy_market(self.symbol, self.quantity)

        order_response = self.client.place_order(self.account_hash, order)

        if order_response:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        Notification.send_sms_via_email(message)

    def sell(self):
        if self.price:
            order = equity_sell_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_sell_market(self.symbol, self.quantity)

        order_response = self.client.place_order(self.account_hash, order)

        if order_response:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        Notification.send_sms_via_email(message)

    def cancel(self):
        self.client.cancel_order(self.order_id, self.account_hash)

        self.get_order()

    def get_order(self):
        """
        Sets an order object to the details retreived by getting the order by its order_id

        Parameters:
            self.order_id (str): The order_id to retrieve.
            self.client (schwab.auth.Client): The client object to access an account.
            self.account_hash (str): The hashed account id given by schwab.

        Returns:
            None: Sets the object self values to the order details retrieved.
        """
        resp = self.client.get_order(self.order_id, self.account_hash)
        assert resp.status_code == httpx.codes.OK
        order_details = resp.json()

        if order_details:
            self.symbol = order_details["orderLegCollection"][0]["instrument"]["symbol"]
            self.quantity = order_details["quantity"]
            self.filled_quantity = order_details["filledQuantity"]
            self.remaining_quantity = order_details["remainingQuantity"]
            self.order_id = order_details["orderId"]
        else:
            raise ValueError("Order_ID is not a valid ID for any Order")

    @staticmethod
    def get_all_orders(
        account_hash: str, client: Client, status: Client.Order.Status = None
    ):
        return client.get_orders_for_account(account_hash, status=status).json()


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


def cancel_all_open_orders(client: Client, account_hash: str):
    open_orders = Order.get_all_orders(
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
