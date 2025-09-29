import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to_email: str, subject: str, html_body: str) -> None:
    host = os.getenv("EMAIL_HOST", "")
    port = int(os.getenv("EMAIL_PORT", "587"))
    username = os.getenv("EMAIL_USER", "")
    password = os.getenv("EMAIL_PASSWORD", "")
    from_email = os.getenv("EMAIL_FROM", username)

    if not (host and username and password and from_email):
        raise RuntimeError("Email not configured: set EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(from_email, [to_email], msg.as_string())

