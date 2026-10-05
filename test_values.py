import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv()

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID", "YOUR_ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def test_august_2026_unemployment():
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0003005865",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "cdArea": "00000",       # Japan
        "limit": "100000"
    }
    
    print("Fetching dataset records...")
    response = requests.get(ESTAT_URL, params=params)
    
    if response.status_code != 200:
        print(f"API Error: Status code {response.status_code}")
        return
        
    root = ET.fromstring(response.content)
    
    print("\n--- AUGUST 2026 UNEMPLOYMENT RATE (BOTH SEXES) ---")
    found = False
    for elem in root.iter():
        if elem.tag.endswith('VALUE') or elem.tag.endswith('value'):
            time_attr = elem.attrib.get('time', '')
            tab = elem.attrib.get('tab', '')
            cat02 = elem.attrib.get('cat02', '')
            cat03 = elem.attrib.get('cat03', '')
            
            # Target August 2026 (2026000808), Tab 02, Unemployment rate (08), Both sexes (0)
            if time_attr == '2026000808' and tab == '02' and cat02 == '08' and cat03 == '0':
                print(f"Time: {time_attr} | Unemployment Rate: {elem.text}% | Attributes: {elem.attrib}")
                found = True
                
    if not found:
        print("Record not found.")

if __name__ == "__main__":
    test_august_2026_unemployment()