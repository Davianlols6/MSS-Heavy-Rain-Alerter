import requests
import datetime
import time
from datetime import datetime, timedelta
import sys, os
from dotenv import load_dotenv
import json

load_dotenv()

weather_alerts = []

def send(message, time):
    url = json.loads(os.environ.get("discord_webhook"))["data"]
    obj = {"embeds": [{"title": "Heavy Rain Warning","url": "http://www.weather.gov.sg/warning-heavy-rain/","color": 16715535,"fields": [ {"name": "Message", "value": "\n\n".join(message)}], "author": {"name": "Meteorological Service Singapore (MSS)", "url": "http://www.weather.gov.sg/home"}, "footer": {"text": "Issued at"}, "timestamp": time, "thumbnail": {"url": "http://www.weather.gov.sg/wp-content/themes/wiptheme/assets/img/mss-logo.png"}}],"username": "Bot" }
    
    for items in url:
        print(items)
        requests.post(items, json=obj)

def Check():
    global weather_alerts

    try:
        c = requests.post("http://www.weather.gov.sg/wp-content/themes/wiptheme/page-functions/functions-ajax-warningbar.php", timeout=10).json()
        be = []
        for items in c:
            for item2 in items['warnings']:
                be.append(item2['title'].replace('<br>', '\n'))
                be.append("Issued at " + item2['issueTime'] + " " + item2['issueDate'])
            for item3 in items['advs']:
                be.append(item3)

        bc = []
        if be != weather_alerts:
            weather_alerts = be

            for items in c[0]['warnings'][0]["title"].split('<br>'):
                if items != "":
                    bc.append(items)

            ga1 = datetime.strptime(
                str(datetime.now().year) + " " + c[0]['warnings'][0]["issueDate"] + " " + c[0]['warnings'][0][
                    "issueTime"], "%Y %a,%d %b %I:%M %p") - timedelta(hours=8)
            ga = ga1.isoformat()
            if len(bc) == 1:
                bc.insert(0, '')
            send(bc[1:], str(ga))
        else:
            pass

    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

while True:
    Check()
    time.sleep(30)