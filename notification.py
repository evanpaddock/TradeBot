import os
import smtplib
from email.mime.text import MIMEText


class Notification:
    """A Notification class to send messages using mms or sms via email"""

    def __init__(
        self,
        phone_number: str = None,
        carrier_gateway: str = None,
        sender_email: str = None,
        sender_email_password: str = None,
        host: str = None,
        subject: str = None,
        message: str = None,
    ):
        self.phone_number = phone_number or os.getenv("PHONE_NUMBER")
        self.carrier_gateway = carrier_gateway or os.getenv("CARRIER_GATEWAY")
        self.sender_email = sender_email or os.getenv("SENDER_EMAIL")
        self.sender_email_password = sender_email_password or os.getenv(
            "SENDER_EMAIL_PASSWORD"
        )
        self.host = host or os.getenv("HOST")
        self.subject = subject or "Notification"
        self.message = message or "Some Message"

    def send_text_via_email(self, messages=None, subject=None):
        # Construct the email
        to_number = f"{self.phone_number}@{self.carrier_gateway}"

        final_message = ""
        if type(messages) == list:
            for message in messages:
                final_message += message
        else:
            final_message = message

        msg = MIMEText(final_message)
        msg["From"] = self.sender_email
        msg["To"] = to_number
        msg["Subject"] = subject or self.subject

        try:
            with smtplib.SMTP(self.host, 587) as server:
                server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
                server.login(
                    self.sender_email, self.sender_email_password
                )  # Log in to your Gmail account
                server.sendmail(
                    self.sender_email, to_number, msg.as_string()
                )  # Send the email
                print("Message sent successfully!")
        except Exception as e:
            print(f"Failed to send SMS: {e}")
        finally:
            server.close()
