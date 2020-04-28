import gspread
from google.oauth2.service_account import Credentials

scopes = ['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file('DnD Bot-6c26153fbace.json', scopes=scopes)

gc = gspread.authorize(credentials)

doc  = gc.open_by_url('https://docs.google.com/spreadsheets/d/19mHfL2nXJFRYNVXjgDnDhfb4Zpq8z1YIV1zC1-4kCAI/edit#gid=194376210')

spells_sheet_name = 'Spells'
spells_sheet = doc.worksheet(spells_sheet_name)

try:
    cell = spells_sheet.find("Acid Splash", in_column=1)
    print(spells_sheet.row_values(cell.row))
except gspread.exceptions.CellNotFound as exception:
    print("NO CELL FOUND!")


# print(spells_sheet.acell('A2').value)
