import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv


load_dotenv()


def send_email(to_email, subject, body):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))

    if not sender_email or not sender_password:
        raise ValueError(
            "EMAIL_ADDRESS and EMAIL_PASSWORD "
            "must be configured in the .env file."
        )

    message = EmailMessage()

    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP_SSL(
        smtp_host,
        smtp_port
    ) as server:

        server.login(
            sender_email,
            sender_password
        )

        server.send_message(message)