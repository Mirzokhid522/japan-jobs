import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

ESTAT_APP_ID = os.environ.get("ESTAT_APP_ID", "YOUR_ESTAT_APP_ID")
ESTAT_URL = "https://api.e-stat.go.jp/rest/3.0/app/getStatsData"

def format_time_label(time_str):
    # Converts e.g. "2026000808" -> "Aug. 2026"
    if len(time_str) >= 10:
        year = time_str[:4]
        month_code = time_str[6:8]
        months = {
            "01": "Jan.", "02": "Feb.", "03": "Mar.", "04": "Apr.",
            "05": "May", "06": "Jun.", "07": "Jul.", "08": "Aug.",
            "09": "Sep.", "10": "Oct.", "11": "Nov.", "12": "Dec."
        }
        return f"{months.get(month_code, 'Unknown')} {year}"
    return time_str

@app.route('/api/cpi')
def get_japan_labor_data():
    params = {
        "appId": ESTAT_APP_ID,
        "lang": "E",
        "statsDataId": "0003005865",
        "metaGetFlg": "N",
        "cntGetFlg": "N",
        "cdArea": "00000",  # Japan total
        "limit": "100000"
    }
    
    response = requests.get(ESTAT_URL, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from e-Stat API"}), 500
        
    root = ET.fromstring(response.content)
    
    raw_data = []
    for elem in root.iter():
        if elem.tag.endswith('VALUE') or elem.tag.endswith('value'):
            time_attr = elem.attrib.get('time', '')
            tab = elem.attrib.get('tab', '')
            cat02 = elem.attrib.get('cat02', '')
            cat03 = elem.attrib.get('cat03', '')
            
            # Filter for 2026, Tab 02, Unemployment rate (08), Both sexes (0)
            if time_attr.startswith('2026') and tab == '02' and cat02 == '08' and cat03 == '0':
                raw_data.append({
                    "time": time_attr,
                    "label": format_time_label(time_attr),
                    "value": float(elem.text)
                })
                
    # Sort chronologically
    raw_data = sorted(raw_data, key=lambda x: x["time"])
    
    # Calculate month-over-month change for the bar chart dataset
    japan_series = []
    for i, item in enumerate(raw_data):
        mom_change = 0.0
        if i > 0:
            mom_change = round(item["value"] - raw_data[i-1]["value"], 2)
            
        japan_series.append({
            "label": item["label"],
            "index": item["value"],       # Unemployment Rate (%)
            "yoy": mom_change             # MoM Change points
        })

    return jsonify({"japan": japan_series})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1999, debug=True)