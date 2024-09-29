import os
import smtplib
from email.mime.text import MIMEText
import time


def send_sms_via_email(
    messages,
    phone_number=os.getenv("PHONE_NUMBER"),
    carrier_gateway=os.getenv("CARRIER_GATEWAY"),
    sender_email=os.getenv("SENDER_EMAIL"),
    sender_email_password=os.getenv("SENDER_EMAIL_PASSWORD"),
    host=os.getenv("HOST"),
    subject="Trade Notification",
):
    # Construct the email
    to_number = f"{phone_number}@{carrier_gateway}"

    final_message = ""
    for message in messages:
        final_message += message

    msg = MIMEText(final_message)
    msg["From"] = sender_email
    msg["To"] = to_number
    msg["Subject"] = subject

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
        time.sleep(5)
