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
    
    unemployment_raw = []
    participation_raw = []
    employment_raw = []
    
    for elem in root.iter():
        if elem.tag.endswith('VALUE') or elem.tag.endswith('value'):
            time_attr = elem.attrib.get('time', '')
            tab = elem.attrib.get('tab', '')
            cat02 = elem.attrib.get('cat02', '')
            cat03 = elem.attrib.get('cat03', '')
            
            if time_attr.startswith('2026') and tab == '02' and cat03 == '0':
                item = {
                    "time": time_attr,
                    "label": format_time_label(time_attr),
                    "value": float(elem.text)
                }
                if cat02 == '08':
                    unemployment_raw.append(item)
                elif cat02 == '01':
                    participation_raw.append(item)
                elif cat02 == '13':
                    employment_raw.append(item)
                
    # Sort each series chronologically
    unemployment_series = [{"label": x["label"], "index": x["value"]} for x in sorted(unemployment_raw, key=lambda k: k["time"])]
    participation_series = [{"label": x["label"], "index": x["value"]} for x in sorted(participation_raw, key=lambda k: k["time"])]
    employment_series = [{"label": x["label"], "index": x["value"]} for x in sorted(employment_raw, key=lambda k: k["time"])]

    return jsonify({
        "unemployment": unemployment_series,
        "participation": participation_series,
        "employment": employment_series
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1999, debug=True)