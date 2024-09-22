import smtplib
from email.mime.text import MIMEText
import json

DATA = {}

with open("conf.json") as f:
    DATA = json.load(f)["Notifications"]


# Function to send SMS via email
def send_sms_via_email(
    message,
    phone_number=DATA["PHONE_NUMBER"],
    carrier_gateway=DATA["CARRIER_GATEWAY"],
    sender_email=DATA["SENDER_EMAIL"],
    sender_email_password=DATA["SENDER_EMAIL_PASSWORD"],
    host=DATA["HOST"],
):
    # Construct the email
    to_number = f"{phone_number}@{carrier_gateway}"
    msg = MIMEText(message)
    msg["From"] = sender_email
    msg["To"] = to_number
    msg["Subject"] = "Trade Notification."

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(host=host, port=587)
        server.starttls()
        server.login(sender_email, sender_email_password)

        # Send the email
        server.sendmail(sender_email, to_number, msg.as_string())
        print("SMS sent successfully!")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
    finally:
        server.quit()


message = "Some Message"

# Send the SMS
send_sms_via_email(message)
