"""Email: abstraction + Gmail SMTP + console (pang-dev)."""
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage


class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, html_body: str) -> None: ...


class SmtpEmailSender(EmailSender):
    def __init__(self, user: str, app_password: str,
                 host: str = "smtp.gmail.com", port: int = 587):
        self._user, self._password = user, app_password
        self._host, self._port = host, port

    def send(self, to: str, subject: str, html_body: str) -> None:
        msg = EmailMessage()
        msg["From"] = f"Student Complaint System <{self._user}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content("Buksan ang email na ito sa email client na sumusuporta sa HTML.")
        msg.add_alternative(html_body, subtype="html")
        with smtplib.SMTP(self._host, self._port, timeout=20) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.send_message(msg)


class ConsoleEmailSender(EmailSender):
    """Ipi-print lang sa terminal. Para sa DEV_MODE."""
    def send(self, to: str, subject: str, html_body: str) -> None:
        print(f"\n--- EMAIL (dev) ---\nTo: {to}\nSubject: {subject}\n{html_body}\n-------------------\n")


class ComplaintNotifier:
    """Responsable sa laman ng mga email; ang EmailSender ang bahala sa pagpapadala."""
    def __init__(self, sender: EmailSender):
        self._sender = sender

    def complaint_received(self, complaint) -> None:
        self._sender.send(
            complaint.email,
            f"Complaint Received - {complaint.id}",
            f"<p>Hi {_e(complaint.student_name)},</p>"
            f"<p>Natanggap na namin ang iyong complaint.</p>"
            f"<p><b>Complaint ID: {_e(complaint.id)}</b></p>"
            f"<p>Gamitin ang ID na ito sa <i>Track Complaint</i> page para makita ang status. "
            f"Makakatanggap ka rin ng email kapag na-resolve na ito.</p>",
        )

    def complaint_resolved(self, complaint) -> None:
        remarks = f"<p><b>Remarks ng admin:</b> {_e(complaint.remarks)}</p>" if complaint.remarks else ""
        self._sender.send(
            complaint.email,
            f"Complaint Resolved - {complaint.id}",
            f"<p>Hi {_e(complaint.student_name)},</p>"
            f"<p>Na-resolve na ang iyong complaint (<b>{_e(complaint.id)}</b>).</p>"
            f"{remarks}<p>Salamat sa pag-report.</p>",
        )


def _e(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
