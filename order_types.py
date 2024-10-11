from ast import Eq
import httpx
from schwab.auth import Client
from account import Account
from notification import Notification
import utils


from schwab.orders.equities import (
    equity_buy_limit,
    equity_buy_market,
    equity_sell_limit,
    equity_sell_market,
)


class Equity:
    """A class representing a schwab equity order."""

    status_dict = {status.value: status for status in Client.Order.Status}

    def __init__(
        self,
        account: Account,
        symbol: str = None,
        quantity: int = 0,
        price: str = None,
        order_id: int = None,
        status: Client.Order.Status = None,
        order_like: dict = None,
        notification: Notification = None,
    ):
        """Creates an Order object

        Args:
            account (Account): An active account to pull client and account_hash from.
            symbol (str, optional): Stock symbol. Defaults to None.
            quantity (int, optional): Order amount. Defaults to 0.
            price (str, optional): Order price (If LIMIT order). Defaults to None.
            order_id (int, optional): ID of the order. Defaults to None.
            status (Client.Order.Status, optional): Order status. Defaults to None.
            order_like (dict, optional): A order like object to parse into an order. Defaults to None.
            notification (Notification, optional): A notification object to send message for orders, leave empty to not receive messages. Defults to None.
        """
        self.account = account
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.status = status
        self.notification = notification
        if order_like:
            order = order_like
            self.symbol = order["symbol"]
            self.quantity = order["quantity"]
            self.price = order["price"]

    def __str__(self):
        """Print Current Order Details

        Returns:
            str: A string containing all order fields and values
        """
        message = ""

        message = utils.json_rtp(self)

        return message

    def buy(self):
        """Buys the current order

        Raises:
            TypeError: self.symbol cannot be None
            TypeError: self.quantity cannot be None

        Returns:
            None: if notification is specified.
            str: message of the order status
        """

        if not self.symbol:
            raise TypeError("symbol must be defined.")

        if not self.quantity:
            raise TypeError("quantity must be defined.")

        if self.price:
            order = equity_buy_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_buy_market(self.symbol, self.quantity)

        order_response = self.account.client.place_order(
            self.account.account_hash, order
        )

        if order_response:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        if self.notification:
            self.notification.send_sms_via_email(message)
        else:
            return message

    def sell(self):
        """Sells the current order

        Raises:
            TypeError: self.symbol cannot be None
            TypeError: self.quantity cannot be None

        Returns:
            str: message of the order status
        """
        if not self.symbol:
            raise TypeError("symbol must be defined.")

        if not self.quantity:
            raise TypeError("quantity must be defined.")

        if self.price:
            order = equity_sell_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_sell_market(self.symbol, self.quantity)

        order_response = self.account.client.place_order(
            self.account.account_hash, order
        )

        if order_response:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        if self.notification:
            self.notification.send_sms_via_email(message)
        else:
            return message

    def cancel(self):
        """Cancels the current order

        Raises:
            TypeError: self.order_id cannot be None
            TypeError: self.account_hash cannot be None

        Returns:
            str: message of the order status
        """
        if not self.order_id:
            raise TypeError("order_id must be defined.")

        if not self.account.account_hash:
            raise TypeError("account_hash must be defined.")

        self.account.client.cancel_order(self.order_id, self.account.account_hash)
        self.get_order()

        if self.filled_quantity > 0:
            message = f"Order {self.order_id} for {self.quantity} shares of {self.symbol} was cancelled, but {self.filled_quanitity} were filled and {self.remaining_quantity} were remianing."
        else:
            message = f"Order {self.order_id} for {self.quantity} shares of {self.symbol} was cancelled"

        if self.notification:
            self.notification.send_sms_via_email(message)
        else:
            return message

    def get_order(self):
        """Sets current object to the order defined by it's order_id

        Raises:
            TypeError: self.order_id cannot be None
            TypeError: self.client cannot be None
            ValueError: There was an error processing the order retrieved.
        """
        if not self.order_id:
            raise TypeError("order_id must be defined.")
        if not self.account.client:
            raise TypeError("client must be defined.")

        resp = self.account.client.get_order(self.order_id, self.account.account_hash)
        assert resp.status_code == httpx.codes.OK
        order_details = resp.json()

        if order_details:
            self.symbol = order_details["orderLegCollection"][0]["instrument"]["symbol"]
            self.quantity = order_details["quantity"]
            self.filled_quantity = order_details["filledQuantity"]
            self.remaining_quantity = order_details["remainingQuantity"]
        else:
            raise ValueError(f"There was an error processing the order")

    @staticmethod
    def get_all_orders(
        account_hash: str, client: Client, status: Client.Order.Status = None
    ):
        """Gets all orders for an account. Can grab optionally by status.

        Args:
            account_hash (str): Hashed account ID value
            client (schwab.auth.Client): schwab account client
            status (Client.Order.Status, optional): Order status to retrieve. Defaults to None.

        Returns:
            list (Order): A list of all retrieved orders
        """
        resp = client.get_orders_for_account(account_hash, status=status)
        assert resp.status_code == httpx.codes.OK
        orders = resp.json()
        return orders

    @staticmethod
    def cancel_all_open_orders(client: Client, account_hash: str):
        """Cancels all pending orders

        Args:
            client (schwab.auth.Client): schwab client
            account_hash (str): Hashed account ID value

        Returns:
            list (str): A list of order cancellation messages
        """
        open_orders = Equity.get_all_orders(
            account_hash, client, client.Order.Status.WORKING
        )
        messages = []
        if len(open_orders) == 0:
            messages.append(f"No open orders to be closed.")
        else:
            for open_order in open_orders:
                order = Equity(
                    client,
                    account_hash,
                    open_order["orderLegCollection"][0]["instrument"]["symbol"],
                    open_order["quantity"],
                    open_order["price"],
                    open_order["orderId"],
                    open_order["status"],
                )

                message = order.cancel()
                messages.append(message + "<br><br>")

        return messages
