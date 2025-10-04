import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SheetsLogger:
    def __init__(self, spreadsheet_name):
    	import os
    	import json
    
    	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    	# Читаем credentials из переменной окружения
    	creds_json = os.getenv('GOOGLE_CREDENTIALS')
    	if creds_json:
            creds_dict = json.loads(creds_json)
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
        # Локально читаем из файла
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    
        client = gspread.authorize(creds)
        self.sheet = client.open(spreadsheet_name).sheet1
    
    def log_message(self, username, user_id, question, answer):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sheet.append_row([timestamp, username, user_id, question, answer[:500]])
