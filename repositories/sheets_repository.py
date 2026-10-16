"""Google Sheets bilang database (gamit ang gspread + service account)."""
from typing import List, Optional

import gspread

from models.complaint import Complaint
from repositories.base import ComplaintRepository


class GoogleSheetsComplaintRepository(ComplaintRepository):
    def __init__(self, credentials_file: str, sheet_id: str, worksheet_name: str):
        client = gspread.service_account(filename=credentials_file)
        spreadsheet = client.open_by_key(sheet_id)
        try:
            self._ws = spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            self._ws = spreadsheet.add_worksheet(worksheet_name, rows=1000, cols=len(Complaint.HEADERS))
        self._ensure_headers()

    def _ensure_headers(self) -> None:
        if self._ws.row_values(1) != Complaint.HEADERS:
            self._ws.update(range_name="A1", values=[Complaint.HEADERS])

    def add(self, complaint: Complaint) -> None:
        self._ws.append_row(complaint.to_row(), value_input_option="RAW")

    def get(self, complaint_id: str) -> Optional[Complaint]:
        cell = self._ws.find(complaint_id, in_column=1)
        if cell is None:
            return None
        values = self._ws.row_values(cell.row)
        values += [""] * (len(Complaint.HEADERS) - len(values))
        return Complaint.from_record(dict(zip(Complaint.HEADERS, values)))

    def list_all(self) -> List[Complaint]:
        records = self._ws.get_all_records(expected_headers=Complaint.HEADERS)
        return [Complaint.from_record(r) for r in records]

    def update(self, complaint: Complaint) -> None:
        cell = self._ws.find(complaint.id, in_column=1)
        if cell is None:
            raise KeyError(complaint.id)
        self._ws.update(range_name=f"A{cell.row}", values=[complaint.to_row()],
                        raw=True)

    def count(self) -> int:
        return max(len(self._ws.col_values(1)) - 1, 0)  # minus header
