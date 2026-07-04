import os

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    os.environ['CREDS_FILE_PATH'],
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(os.environ['GSPREAD_LINK']).sheet1

def save_annotation(record_id, annotator, label, confidence, comment, exec_time):
    rows = sheet.get_all_values()
    target_row = None

    # skip header
    for i, row in enumerate(rows[1:], start=2):
        existing_id = int(row[0])
        existing_annotator = row[1]
        if existing_id == int(record_id) and existing_annotator == annotator:
            target_row = i
            break

    new_data = [
        int(record_id),
        annotator,
        label,
        int(confidence),
        comment,
        datetime.now().isoformat(),
        exec_time
    ]

    if target_row:
        # update existing row
        sheet.update(f"A{target_row}:G{target_row}", [new_data])
    else:
        # append new row
        sheet.append_row(new_data)

def load_annotations(annotator):
    records = sheet.get_all_records()
    return [x for x in records if x['annotator']==annotator]