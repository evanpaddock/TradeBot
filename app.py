import os
from dotenv import load_dotenv
import Order, Account, Notification, Utils  # Importing custom modules used in the application
from flask import (
    Flask,
    make_response,
    jsonify,
    request,
)  # Flask utilities for response handling

# Initialize Flask application
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv(".env")

# Setup client and account_hash by calling the Account setup function
client, account_hash = Account.setup()

# Example of sending an SMS notification (currently commented out)
# Notification.send_sms_via_email(f"App successfully running for client: {client.get_account_numbers().json()[0]['accountNumber']}")


@app.route("/")
def index():
    """
    Root endpoint that displays a welcome message for TradeBot.

    Returns:
        str: HTML string welcoming the user to TradeBot.
    """
    return "<h1>Welcome to TradeBot!</h1>"


@app.route("/Market/Positions/Current")
def open_positions():
    """
    Endpoint to get the current market positions.

    Currently, this is a placeholder endpoint that returns a 204 (No Content) response.

    Returns:
        Response: A 204 No Content response, indicating no data is available.
    """
    return make_response("", 204)


@app.route("/Market/Time/Current")
def current_time():
    """
    Endpoint to get the current market hours.

    The market hours are retrieved via a utility function and returned as a JSON response.
    If the hours list contains more than two elements, they are returned as-is. Otherwise,
    the start and end times are formatted into a string.

    Returns:
        JSON: A JSON object containing the current market hours in the format of a list or formatted string.
    """
    hours = Utils.get_market_hours(client)

    if len(hours) > 2:
        message = hours
    else:
        message = f"{hours[0]} - {hours[1]}"

    return jsonify(message)


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Shutdown the Flask application"""
    KEY = request.form["KEY"]
    if KEY == os.getenv("SHUTDOWN_KEY"):
        shutdown_func = request.environ.get("werkzeug.server.shutdown")
        if shutdown_func is None:
            # If not running on Werkzeug, fallback to exit the process
            os._exit(0)  # This forces the app to exit
        shutdown_func()
    else:
        return "Invalid Key", 403


# Main entry point of the application
if __name__ == "__main__":
    app.run(debug=True)  # Start the Flask app in debug mode
    print("Ending TradeBot...")  # Print a message when the app is stopped
