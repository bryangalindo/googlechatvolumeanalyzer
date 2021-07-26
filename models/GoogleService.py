from googleapiclient.discovery import build


class GoogleService:
    def __init__(self, credentials, product, version):
        self.credentials = credentials
        self.product = product
        self.version = version
        self.service = None
    
    def insert_row_into_spreadsheet(self, body, spreadsheet_id, sheet_range, value_input_option):
        self.__create_service()
        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_range,
            valueInputOption=value_input_option,
            body=body,).execute()
        
    def __create_service(self):
        self.service = build(self.product, self.version, credentials=self.credentials)
