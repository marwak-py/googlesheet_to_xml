import sys
import re
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import xml.etree.ElementTree as ET


# user should give me the sheet url
spreadsheet_url = sys.argv[1]
# Extract the spreadsheet ID from the given url
match = re.search(r'/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
if match:
    spreadsheet_id = match.group(1)
else:
    raise ValueError("Invalid Google Spreadsheet URL")

### Read Google sheet
def read_translations_from_sheet(spreadsheet_id):
    # Authenticate and get the Sheets service
    sheets_service, _ = authenticate_google_apis()

    # 1/ Read the values from the specified range
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Sheet1!C2:C'
    ).execute()

    values = result.get('values', [])
    # 2/ Get the spreadsheet title (metadata)
    sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    title = sheet_metadata.get('properties', {}).get('title', 'Untitled Spreadsheet')
    return values, title
# Authenticate Google API
def authenticate_google_apis():
    credentials_file = 'hindawi-foundation-readers-credentials.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=SCOPES)

    sheets_service = build('sheets', 'v4', credentials=credentials)
    return sheets_service, None

### Creat Translated XML
def parse_source_xml(trans_data, sheet_name):
    xml_id = sheet_name.split('_')[0]
    xml_name = xml_id + '.xml'
    translated_lang = sheet_name.split('_')[2]
    # this tool depends on the existance of xml file on the local directory in 'source_xml' named by the sheet_name
    for root_dir, dirs, files in os.walk('source_xml'):
        if xml_name in files:
            tree = ET.parse(os.path.join(root_dir, xml_name))
            root = tree.getroot()
            # 1/ replace lang value with the translated lang
            root.set('lang', translated_lang)
            # 2/ replace title and metatitle
            root.find('.//meta_title').text = trans_data[2][0]
            # 3/ replace summary
            root.find('.//summary').text = trans_data[0][0]
            root.find('body/*[1]/title').text = trans_data[2][0]
            # 4/ replace p
            data_index = 3
            for p_tag in root.findall('.//p'):
                if data_index < len(trans_data):
                    # Replace the text of <p> tag with corresponding text_data value
                    p_tag.text = trans_data[data_index][0]
                    data_index += 1
            # 5/ write the result in external xml
            output_file_name = xml_id + '_' + translated_lang + '.xml'
            tree.write(os.path.join(f'translated_xml_{translated_lang}', output_file_name), encoding='utf-8', xml_declaration=True)

#USAGE
tran_data, sheet_name = read_translations_from_sheet(spreadsheet_id)

print(tran_data)
parse_source_xml(tran_data, sheet_name)
