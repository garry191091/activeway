import gspread
from django.conf import settings

gc = gspread.service_account_from_dict(settings.GOOGLE_API_CREDENTIALS)
spreadsheet = gc.open_by_key(settings.GOOGLE_API_SPREADSHEET)
worksheet = spreadsheet.worksheet("Import Data")


def lookup_code(code: str):
    found = worksheet.find(code, in_column=1)
    return found.row if found else None


def update_entry(range, new_value):
    worksheet.update(range, new_value, value_input_option="user_entered")
    return True


def create_entry(values: list):
    worksheet.append_row(values, value_input_option="user_entered")
