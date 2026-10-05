import os
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def inspect_dataset_metadata():
    if not ESTAT_APP_ID or ESTAT_APP_ID == "YOUR_ESTAT_APP_ID":
        print("Error: ESTAT_APP_ID is not set in your .env file.")
        return

    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0003005865",
        "metaGetFlg": "Y",
        "cntGetFlg": "N"
    }
    
    print("Fetching metadata and structure for dataset 0003005865...")
    response = requests.get(ESTAT_URL, params=params)
    
    print(f"Response Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"API Error Response: {response.text}")
        return
    
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return
    
    print("\n--- AVAILABLE CLASSIFICATIONS & CODES ---")
    for class_obj in root.iter():
        if class_obj.tag.endswith('CLASS_OBJ') or class_obj.tag.endswith('classObj'):
            obj_id = class_obj.attrib.get('id')
            obj_name = class_obj.attrib.get('name')
            print(f"\n[Classification ID: {obj_id}] Name: {obj_name}")
            
            for child in class_obj:
                if child.tag.endswith('CLASS') or child.tag.endswith('class'):
                    c_code = child.attrib.get('code')
                    c_name = child.attrib.get('name')
                    print(f"  -> Code: {c_code} | Name: {c_name}")

if __name__ == "__main__":
    inspect_dataset_metadata()