"""Abstraction: alam ng service kung ano ang kailangan, hindi kung saan nakalagay ang data."""
from abc import ABC, abstractmethod
from typing import List, Optional

from models.complaint import Complaint


class ComplaintRepository(ABC):
    @abstractmethod
    def add(self, complaint: Complaint) -> None: ...

    @abstractmethod
    def get(self, complaint_id: str) -> Optional[Complaint]: ...

    @abstractmethod
    def list_all(self) -> List[Complaint]: ...

    @abstractmethod
    def update(self, complaint: Complaint) -> None: ...

    @abstractmethod
    def count(self) -> int: ...
