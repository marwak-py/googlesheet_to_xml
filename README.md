# googlesheet_to_xml
fetch data from google sheet Id and import it in XML file with structure similar to input one. 
# input parameters
googlsheet url (command)
xml file (exists on a local directory *source_xml* named by the sheet_name), where sheet name will be fetched in the runtime.
# output
xml file named by *xml_id_[translated_lang].xml* in local directory named by *translated_xml_[translated_lang]*
# command
python booktime_translation_xml.py [spreadsheet_url]
