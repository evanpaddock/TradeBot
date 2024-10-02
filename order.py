import httpx
from schwab.auth import Client
from schwab.orders.equities import (
    equity_buy_limit,
    equity_buy_market,
    equity_sell_limit,
    equity_sell_market,
)
import notification


class Order:
    """
    A class representing a schwab order.

    Attributes:
        client? (schwab.auth.Client): The client account.
        account_hash? (int): The hashed ID value of the account.
        symbol? (str): The symbol of the share.
        quantity? (int): The quantity of shares.
        price? (float): The limit price of the order.
        order_id? (int): The ID of the order.
        status? (Client.Order.Status): The status of the order.
    """

    def __init__(
        self,
        client: Client=None,
        account_hash: str = None,
        symbol: str = None,
        quantity: int = 0,
        price: str = None,
        order_id: int = None,
        status: Client.Order.Status = None,
    ):
        """
        Initializes an Order object.

        Parameters:
            client? (schwab.auth.Client): The client account.
            account_hash? (int): The hashed ID value of the account.
            symbol? (str): The symbol of the share.
            quantity? (int): The quantity of shares.
            price? (str): The limit price of the order.
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
        if not self.symbol:
            raise TypeError("symbol must be defined.")
        
        if not self.quantity:
            raise TypeError("quantity must be defined.")
        
        if self.price:
            order = equity_buy_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_buy_market(self.symbol, self.quantity)

        order_response = self.client.place_order(self.account_hash, order)

        if order_response:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to buy {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        return message

    def sell(self):
        if not self.symbol:
            raise TypeError("symbol must be defined.")
        
        if not self.quantity:
            raise TypeError("quantity must be defined.")
        if self.price:
            order = equity_sell_limit(self.symbol, self.quantity, self.price)
        else:
            order = equity_sell_market(self.symbol, self.quantity)

        order_response = self.client.place_order(self.account_hash, order)

        if order_response:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol}{f' at {self.price}' if self.price != None else ''} was sent successful."
        else:
            message = f"Order to sell {self.quantity} share{'s' if self.quantity > 1 else ''} of {self.symbol} has failed. Please check the application for a more specific error."

        return message

    def cancel(self):
        if not self.order_id:
            raise TypeError("order_id must be defined.")
        
        if not self.account_hash:
            raise TypeError("account_hash must be defined.")
        
        self.client.cancel_order(self.order_id, self.account_hash)
        self.get_order()
        
        if self.filled_quanitity > 0:
            message = f"Order {self.order_id} for {self.quantity} shares of {self.symbol} was cancelled, but {self.filled_quanitity} were filled and {self.remaining_quantity} were remianing."
        else:
            message = f"Order {self.order_id} for {self.quantity} shares of {self.symbol} was cancelled"

        return message
        

    def get_order(self):
        """
        Sets an order object to the details retreived by getting the order by its order_id.

        Parameters:
            self.order_id (str): The order_id to retrieve.
            self.client (schwab.auth.Client): The client object to access an account.
            self.account_hash (str): The hashed account id given by schwab.

        Returns:
            None: Sets the object self values to the order details retrieved.
        """
        if not self.order_id:
            raise TypeError("order_id must be defined.")
        
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
            raise ValueError(f"Order_ID: {self.order_id} is not a valid ID for any Order.")

    @staticmethod
    def get_all_orders(
        account_hash: str, client: Client, status: Client.Order.Status = None
    ):
        resp = client.get_orders_for_account(account_hash, status=status)
        assert resp.status_code == httpx.codes.OK
        orders = resp.json()
        return orders
    
    @staticmethod
    def cancel_all_open_orders(client: Client, account_hash: str):
        open_orders = Order.get_all_orders(
            account_hash, client, client.Order.Status.PENDING_ACTIVATION
        )
        messages = []
        if len(open_orders) == 0:
            messages.append(f"No open orders to be closed.")
        else:
            for open_order in open_orders:
                order = Order(client, account_hash, open_order["orderLegCollection"][0]["instrument"]["symbol"], open_order["quantity"],open_order["price"] ,open_order["order_id"], open_order["status"])
                
                message = order.cancel()
                messages.append(message + "<br><br>")
                
        notification.send_sms_via_email(messages)