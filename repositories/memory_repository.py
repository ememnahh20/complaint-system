"""Pang-test at DEV_MODE: walang Google na kailangan."""
from typing import Dict, List, Optional

from models.complaint import Complaint
from repositories.base import ComplaintRepository


class InMemoryComplaintRepository(ComplaintRepository):
    def __init__(self):
        self._items: Dict[str, Complaint] = {}

    def add(self, complaint: Complaint) -> None:
        self._items[complaint.id] = complaint

    def get(self, complaint_id: str) -> Optional[Complaint]:
        return self._items.get(complaint_id)

    def list_all(self) -> List[Complaint]:
        return list(self._items.values())

    def update(self, complaint: Complaint) -> None:
        self._items[complaint.id] = complaint

    def count(self) -> int:
        return len(self._items)
