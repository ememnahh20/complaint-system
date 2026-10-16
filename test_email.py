from config import Config
from services.email_service import SmtpEmailSender

c = Config.from_env()
print("User:", repr(c.gmail_user), "| Password length:", len(c.gmail_app_password))
SmtpEmailSender(c.gmail_user, c.gmail_app_password).send(
    c.gmail_user, "Test", "<p>Gumagana!</p>")
print("Sent!")