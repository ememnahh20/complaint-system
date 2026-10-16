"""Domain model: ang Complaint at ang mga rules nito."""
from datetime import datetime
from enum import Enum

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class Status(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

    @classmethod
    def parse(cls, value: str) -> "Status":
        for status in cls:
            if status.value.lower() == str(value).strip().lower():
                return status
        raise ValueError(f"Invalid status: {value!r}")


class Complaint:
    # Ito rin ang header row (Row 1) ng Google Sheet
    HEADERS = [
        "Complaint ID", "Date Submitted", "Student Name", "Email",
        "Category", "Complaint", "Status", "Admin Remarks", "Date Resolved",
    ]

    def __init__(self, complaint_id, student_name, email, category, message,
                 status=Status.PENDING, submitted_at=None,
                 remarks="", resolved_at=None):
        self._id = complaint_id
        self._student_name = student_name
        self._email = email
        self._category = category
        self._message = message
        self._status = status
        self._submitted_at = submitted_at or datetime.now().replace(microsecond=0)
        self._remarks = remarks
        self._resolved_at = resolved_at

    # --- read-only properties (encapsulation) ---
    id = property(lambda self: self._id)
    student_name = property(lambda self: self._student_name)
    email = property(lambda self: self._email)
    category = property(lambda self: self._category)
    message = property(lambda self: self._message)
    status = property(lambda self: self._status)
    submitted_at = property(lambda self: self._submitted_at)
    remarks = property(lambda self: self._remarks)
    resolved_at = property(lambda self: self._resolved_at)

    @property
    def is_resolved(self) -> bool:
        return self._status == Status.RESOLVED

    # --- behavior ---
    def change_status(self, new_status: Status, remarks: str = "") -> None:
        self._status = new_status
        if remarks:
            self._remarks = remarks
        if new_status == Status.RESOLVED:
            self._resolved_at = self._resolved_at or datetime.now().replace(microsecond=0)
        else:
            self._resolved_at = None

    # --- conversion para sa storage ---
    def to_row(self) -> list:
        return [
            self._id,
            self._submitted_at.strftime(DATE_FORMAT),
            self._student_name,
            self._email,
            self._category,
            self._message,
            self._status.value,
            self._remarks,
            self._resolved_at.strftime(DATE_FORMAT) if self._resolved_at else "",
        ]

    @classmethod
    def from_record(cls, record: dict) -> "Complaint":
        def parse_date(text):
            text = str(text).strip()
            return datetime.strptime(text, DATE_FORMAT) if text else None

        return cls(
            complaint_id=str(record["Complaint ID"]),
            student_name=str(record["Student Name"]),
            email=str(record["Email"]),
            category=str(record["Category"]),
            message=str(record["Complaint"]),
            status=Status.parse(record["Status"] or Status.PENDING.value),
            submitted_at=parse_date(record["Date Submitted"]),
            remarks=str(record["Admin Remarks"]),
            resolved_at=parse_date(record["Date Resolved"]),
        )

    def to_public_dict(self) -> dict:
        """Ligtas na data para sa Track page (walang email o mismong reklamo)."""
        return {
            "complaint_id": self._id,
            "category": self._category,
            "status": self._status.value,
            "date_submitted": self._submitted_at.strftime("%b %d, %Y"),
            "date_resolved": self._resolved_at.strftime("%b %d, %Y") if self._resolved_at else None,
            "remarks": self._remarks,
        }
