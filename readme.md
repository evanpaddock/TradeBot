# TradeBot

**TradeBot** is a Flask-based application that facilitates placing, managing, and cancelling equity orders via an API. The bot interacts with various modules such as `Account`, `Notification`, and `Equity` to handle stock transactions efficiently.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Shutting Down](#shutting-down)
8. [License](#license)

---

## Getting Started

This project provides a simple API to handle equity buy, sell, cancel, and get operations for a trading system.

## Prerequisites

- Python 3.x
- git

Ensure you have a Python environment set up on your machine.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/evanpaddock/TradeBot.git
   cd tradebot
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate your virtual environment for the project.
   For Mac
   ```bash
   source .venv/bin/activate
   ```
   For Windows
   ```bash
   .venv/Scripts/activate
   ```
4. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root to store your environment variables. This file is used to configure sensitive data such as API keys, account details, and notification settings.

## Configuration

You'll need to set up the following environment variables in your `.env` file:

```
# Environment variables
    # TradeBot
APP_KEY=
APP_SECRET=
CALLBACK_* URL=
TOKEN_PATH=
ORDERS_PATH=
    # Notification
PHONE_NUMBER=
CARRIER_GATEWAY=
SENDER_EMAIL=
SENDER_EMAIL_PASSWORD=
HOST=
    # Flask App
SHUTDOWN_KEY=
```

## Usage

### Start the Flask server:

```bash
python app.py
```

The application will be running on http://127.0.0.1:5000/. You can interact with it via the provided API endpoints.

## API Endpoints

1. Home
   - URL: /
   - Method: GET
   - Description: A simple welcome page for TradeBot.
   - Response: Returns an HTML welcome message.
2. Buy Equity Order
   - URL: /Order/Equity/Buy
   - Method: POST
   - Description: Places a new buy order.
   - Request Body: JSON containing order details with type "BUY".
   - Response: Success or failure message.
3. Sell Equity Order
   - URL: /Order/Equity/Sell
   - Method: POST
   - Description: Places a new sell order.
   - Request Body: JSON containing order details with type "SELL".
   - Response: Success or failure message.
4. Get Equity Orders
   - URL: /Order/Equity/Get
   - Method: POST
   - Description: Retrieves all equity orders or filters based on status.
   - Request Body: JSON containing order details with type "Get".
   - Response: A list of orders.
5. Cancel Equity Order
   - URL: /Order/Equity/Cancel
   - Method: POST
   - Description: Cancels an equity order based on order ID.
   - Request Body: JSON containing order details with type "CANCEL" and order_id.
   - Response: Success or failure message.
6. Shutdown
   - URL: /shutdown
   - Method: POST
   - Description: Shuts down the Flask application.
   - Request Body: JSON with SHUTDOWN_KEY matching the environment variable.
   - Response: A success or error message based on key validation.

## Shutting Down

To shut down the application, send a POST request to /shutdown with a JSON payload containing the correct shutdown key.

Example:

```
{
"SHUTDOWN_KEY": "<your_shutdown_key>"
}
```

## License

This project is licensed under the MIT License.
