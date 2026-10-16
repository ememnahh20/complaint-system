"""Business logic. Walang Flask, walang Google dito, kaya madaling i-test."""
import logging
import re
import secrets
import string
import threading
from datetime import datetime
from typing import List, Optional

from models.complaint import Complaint, Status
from repositories.base import ComplaintRepository
from services.email_service import ComplaintNotifier

log = logging.getLogger(__name__)

CATEGORIES = ["Facilities", "Academic", "Faculty / Staff",
              "Bullying / Harassment", "Other"]
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    pass


class ComplaintNotFound(Exception):
    pass


class ComplaintService:
    def __init__(self, repository: ComplaintRepository, notifier: ComplaintNotifier):
        self._repo = repository
        self._notifier = notifier
        self._lock = threading.Lock()  # iwas duplicate ID kapag sabay ang submit

    # ---------- Student ----------
    def submit(self, name: str, email: str, category: str, message: str) -> dict:
        name, email, message = (name or "").strip(), (email or "").strip(), (message or "").strip()
        if len(name) < 2:
            raise ValidationError("Ilagay ang buong pangalan mo.")
        if not EMAIL_PATTERN.match(email):
            raise ValidationError("Hindi valid ang email address.")
        if category not in CATEGORIES:
            raise ValidationError("Pumili ng category.")
        if len(message) < 10:
            raise ValidationError("Ilarawan nang mas detalyado ang complaint (min. 10 characters).")

        with self._lock:
            complaint = Complaint(self._generate_id(), name, email, category, message)
            self._repo.add(complaint)

        email_sent = self._safe_notify(self._notifier.complaint_received, complaint)
        return {"complaint_id": complaint.id, "email_sent": email_sent}

    def track(self, complaint_id: str) -> dict:
        complaint = self._repo.get((complaint_id or "").strip().upper())
        if complaint is None:
            raise ComplaintNotFound(complaint_id)
        return complaint.to_public_dict()

    # ---------- Admin ----------
    def list_complaints(self, status: Optional[str] = None) -> List[Complaint]:
        items = self._repo.list_all()
        if status:
            wanted = Status.parse(status)
            items = [c for c in items if c.status == wanted]
        return sorted(items, key=lambda c: c.submitted_at, reverse=True)

    def update_status(self, complaint_id: str, new_status: str, remarks: str = "") -> dict:
        try:
            status = Status.parse(new_status)
        except ValueError as exc:
            raise ValidationError(str(exc))

        complaint = self._repo.get(complaint_id)
        if complaint is None:
            raise ComplaintNotFound(complaint_id)

        was_resolved = complaint.is_resolved
        complaint.change_status(status, (remarks or "").strip())
        self._repo.update(complaint)

        email_sent = None
        if complaint.is_resolved and not was_resolved:  # isang beses lang magpapadala
            email_sent = self._safe_notify(self._notifier.complaint_resolved, complaint)
        return {"complaint_id": complaint.id, "status": status.value, "email_sent": email_sent}

    def stats(self) -> dict:
        items = self._repo.list_all()
        return {
            "total": len(items),
            **{s.value: sum(1 for c in items if c.status == s) for s in Status},
        }

    # ---------- internal ----------
    def _generate_id(self) -> str:
        seq = self._repo.count() + 1
        token = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        return f"CMP-{datetime.now().year}-{seq:04d}-{token}"

    @staticmethod
    def _safe_notify(send_fn, complaint) -> bool:
        """Kapag pumalya ang email, hindi mawawala ang complaint."""
        try:
            send_fn(complaint)
            return True
        except Exception:
            log.exception("Email failed for %s", complaint.id)
            return False
