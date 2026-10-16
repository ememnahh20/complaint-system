import smtplib
from config import Config

c = Config.from_env()
print("User:", repr(c.gmail_user), "| Password length:", len(c.gmail_app_password))

print("\n=== Port 587 (STARTTLS) ===")
try:
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
    s.starttls()
    s.login(c.gmail_user, c.gmail_app_password)
    print("587 OK")
    s.quit()
except Exception as e:
    print("587 FAILED:", repr(e))

print("\n=== Port 465 (SSL) ===")
try:
    s = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)
    s.login(c.gmail_user, c.gmail_app_password)
    print("465 OK")
    s.quit()
except Exception as e:
    print("465 FAILED:", repr(e))