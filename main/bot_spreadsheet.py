import gspread
from google.oauth2.service_account import Credentials

scopes = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']

DB_SS_URL = 'https://docs.google.com/spreadsheets/d/19mHfL2nXJFRYNVXjgDnDhfb4Zpq8z1YIV1zC1-4kCAI/edit#gid=194376210'

credentials = Credentials.from_service_account_file('google_sa_key.json', scopes=scopes)
gc = None
doc = None

def init():
    global gc, doc
    gc = gspread.authorize(credentials)
    doc = gc.open_by_url(DB_SS_URL)



def search_spells(term):
    global doc
    SHEET_NAME = "Spells"
    
    sheet = doc.worksheet(SHEET_NAME)

    try:
        cell = sheet.find(term, in_column=1)
        result = {
            "found":True,
            "value": sheet.row_values(cell.row)
        }
    except gspread.exceptions.CellNotFound:
        result = {
            "found": False
        }
    return result
