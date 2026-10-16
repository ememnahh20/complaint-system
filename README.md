# Student Complaint System

Python (Flask, OOP/OOD) + HTML + Google Sheets bilang database.

## Structure
```
app.py                       Flask routes lang
config.py                    settings mula sa .env
models/complaint.py          Complaint class at Status enum
repositories/                base.py (abstract), sheets_repository.py, memory_repository.py
services/complaint_service.py  business logic
services/email_service.py      EmailSender (abstract), SmtpEmailSender, ComplaintNotifier
templates/, static/          HTML at CSS
tests/                       unit tests
```

## 1. Subukan muna nang walang Google (DEV_MODE)
```
pip install -r requirements.txt
cp .env.example .env        # tapos gawing DEV_MODE=true
python app.py
```
Buksan ang http://127.0.0.1:5000. Ang mga email ay lalabas sa terminal.
Admin: http://127.0.0.1:5000/admin (password = ADMIN_PASSWORD sa .env)

## 2. I-connect sa Google Sheets
1. Pumunta sa https://console.cloud.google.com, gumawa ng project.
2. I-enable ang **Google Sheets API** at **Google Drive API**.
3. IAM & Admin, Service Accounts, Create. Pagkatapos: Keys, Add key, JSON.
   I-save ang file bilang `credentials.json` sa project folder.
4. Gumawa ng bagong Google Sheet. Kopyahin ang ID sa URL (`/d/<ID>/edit`) at ilagay sa `GOOGLE_SHEET_ID`.
5. I-**Share** ang Sheet sa `client_email` na nasa credentials.json (Editor access).
6. Ang headers sa Row 1 ay awtomatikong ginagawa ng app.

## 3. Gmail para sa email
1. I-on ang 2-Step Verification sa Google account.
2. Google Account, Security, App passwords. Gumawa ng isa.
3. Ilagay sa `.env`: `GMAIL_USER` at `GMAIL_APP_PASSWORD`.

Itakda ang `DEV_MODE=false` at patakbuhin ang `python app.py`.

## Tests
```
python -m unittest discover -s tests -t .
```

## Notes
- Hindi pwedeng i-commit ang `.env` at `credentials.json` (nasa .gitignore na).
- Ang Complaint ID ay may random na suffix (`CMP-2026-0001-AB12`) para hindi mahulaan ng ibang student.
- Kapag pumalya ang email, nase-save pa rin ang complaint at ipapakita sa student ang ID sa screen.
- Para sa deployment, gamitin ang `gunicorn app:create_app()` at palitan ang SECRET_KEY at ADMIN_PASSWORD.
