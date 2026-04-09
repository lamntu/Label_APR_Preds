import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

creds = Credentials.from_service_account_file(
    "key/labelaprpred-bc2be5b419a3.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key('1wb7nW4vksC7wQQGhD5oMWuVogB-kEi-WVlJ2WuWA4m4').sheet1

# def save_annotation(record_id, annotator, score, comment):
#     sheet.append_row([
#         record_id,
#         annotator,
#         score,
#         comment,
#         datetime.now().isoformat()
#     ])

def save_annotation(record_id, annotator, score, comment):
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
        int(score),
        comment,
        datetime.now().isoformat()
    ]

    if target_row:
        # update existing row
        sheet.update(f"A{target_row}:E{target_row}", [new_data])
    else:
        # append new row
        sheet.append_row(new_data)

def load_annotations(annotator):
    records = sheet.get_all_records()
    return [x for x in records if x['annotator']==annotator]