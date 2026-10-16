from config import Config
from repositories.sheets_repository import GoogleSheetsComplaintRepository

c = Config.from_env()
repo = GoogleSheetsComplaintRepository(c.credentials_file, c.sheet_id, c.worksheet_name)
print("Connected! Rows sa Sheet:", repo.count())