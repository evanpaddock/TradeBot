from schwab.auth import Client


def get_current_positions(client: Client, account_hash: str):
    return client.get_transactions(account_hash)
