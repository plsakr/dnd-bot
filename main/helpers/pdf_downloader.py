from pydrive.auth import GoogleAuth, ServiceAccountCredentials
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
scope = ['https://www.googleapis.com/auth/drive']
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name('DnD Bot-6c26153fbace.json', scope)
drive = GoogleDrive(gauth)


def download_pdf(id, target):
    global drive
    file = drive.CreateFile({'id': id})
    print("Found a file in google drive!")
    file.GetContentFile(target)