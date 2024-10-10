from schwab.auth import Client, easy_client
import os


class Account:
    def __init__(self, client: Client = None, account_hash: str = None) -> None:
        if client and account_hash:
            self.client = client
            self.account_hash = account_hash
        else:
            self.client, self.account_hash = Account._setup()

    @staticmethod
    def _setup():
        client = Account._get_client()
        account_hash = Account._get_account_hash(client)
        return (client, account_hash)

    @staticmethod
    def _get_account_hash(client: Client) -> any:
        accountHash = client.get_account_numbers().json()[0]["hashValue"]
        return accountHash

    @staticmethod
    def _get_client():
        """Get's a client object to access a schwab account.

        Returns:
            (AsyncClient | Client): Schwab Client
        """
        api_key = os.getenv("APP_KEY")
        app_secret = os.getenv("APP_SECRET")
        callback_url = os.getenv("CALLBACK_URL")
        token_path = os.getenv("TOKEN_PATH")
        try:
            client = easy_client(api_key, app_secret, callback_url, token_path)
            return client
        except:
            os.remove(token_path)
            client = easy_client(api_key, app_secret, callback_url, token_path)
            return client
