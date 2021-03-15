import logging
import random
from datetime import time

import gspread
from gspread import SpreadsheetNotFound

from google.oauth2.service_account import Credentials



scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    r'C:\Users\Aleksandr\.gkeys\mgmoose.json',
    scopes=scopes
)




class GoogleTable():
    def __init__(self,docname="DefaultTable", headers=None):
        self.docname = docname
        self.gc = gspread.authorize(credentials)

        try:
            self.sh = self.gc.open(docname)
        except SpreadsheetNotFound:
            self.sh = self.gc.create(docname)
        self.sh.share('bambruysk@gmail.com', perm_type='user', role='writer')
        self.ws = self.sh.sheet1
        self.ws.clear()
        for i,h in enumerate(headers):
            self.ws.update_cell(1, i+1, h)
        self.last_pos = 2 if headers else 1

    def clean(self):
        """
            clean all rows, save header
        """
        self.ws.delete_rows(2, self.last_pos)

    def write_header(self,header):
        self.ws.delete_row(1)
        for i,h in enumerate(headers):
            self.ws.update_cell(1, i+1, h)
            self.last_pos = 2

    def add_row(self, row):
        self.ws.insert_row(row)
        self.last_pos += 1

    def add_rows(self, rows):
        self.ws.insert_rows(rows,row=self.last_pos)
        self.last_pos += len(rows)



    def share(self, email:str):
        self.sh.share(email, perm_type='user', role='writer')
        



## test


