#  pip install google-api-python-client oauth2client
import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from settings import SHEETS_ID
"""
Подключение апи
"""

CREDENTIALS_FILE = 'creds.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)


# чтение из таблицы
async def read_sheets(sheets_name, dimension):
    values = service.spreadsheets().values().get(
        spreadsheetId=SHEETS_ID,
        range=f'{sheets_name}!A2:H',
        majorDimension=dimension,
    ).execute()
    try:
        values = values['values']
    except KeyError:
        values = []
    return values


# добавление в таблицу
async def append_sheets(sheets_name, data):
    body = {
        'values':
            [[data["date"],
              data["ticker"],
              data["name"],
              data["operation_type"],
              data["price"],
              data["payment"],
              data["quantity"],
              data["currency"]]]
    }
    result = service.spreadsheets().values().append(spreadsheetId=SHEETS_ID, range=f"{sheets_name}!A1:I1",
                                                    valueInputOption="USER_ENTERED", body=body).execute()
    print(result)