import requests
import datetime
import telegram
import config
import time
from telegram import ext
from datetime import datetime, timedelta
import sys, os

prev_observation_time = ""
prev_rain_time = ""
raining = False
weather_alerts = []

send_bad_fore = False

weathersymbols = {
    'PS': 'Passing Showers',
    'WD': 'Windy',
    'FW': 'Fair and Warm',
    'SH': 'Showers',
    'FN': 'Fair',
    'FA': 'Fair',
    'PC': 'Partly Cloudy',
    'TL': 'Thundery Showers',
    'HG': 'Heavy Thundery Showers with Gusty Winds',
    'LS': 'Light Showers',
    'PN': 'Partly Cloudy',
    'CL': 'Cloudy',
    'RA': 'Moderate Rain',
    'LR': 'Light Rain',
    'HT': 'Heavy Thundery Showers'
}

bad_fore = ['PS', "SH", "TL", "HG", "LS", "RA", "LR", "HT"]

wanted = ["S77", "S120", "S92", "S90", "S79", "S31", "S71", "S111", "S118", "S72", "S46", "S60", "S50", "S07", "S119", "S123", "S116"]

updater = telegram.ext.Updater(token=config.telegram_bot_token, use_context=True)

distance = {
    "S77": "0.34km",
    "S120": "1.67km",
    "S92": "2.73km",
    "S90": "2.77km",
    "S79": "3.03km",
    "S31": "3.08km",
    "S71": "3.24km",
    "S111": "3.34km",
    "S118": "3.99km",
    "S72": "4.85km",
    "S46": "5.07km",
    "S60": "5.36km",
    "S50": "5.52km",
    "S07": "5.73km",
    "S119": "5.76km",
    "S123": "5.98km",
    "S116": "6.39km",
}

prev_rain_data = {
    "S77": 0.0,
    "S120": 0.0,
    "S92": 0.0,
    "S90": 0.0,
    "S79": 0.0,
    "S31": 0.0,
    "S71": 0.0,
    "S111": 0.0,
    "S118": 0.0,
    "S72": 0.0,
    "S46": 0.0,
    "S60": 0.0,
    "S50": 0.0,
    "S07": 0.0,
    "S119": 0.0,
    "S123": 0.0,
    "S116": 0.0,
}

station_name = {
    'S07': 'Bishan',
    'S111': 'City (Newton)',
    'S116': 'Queenstown (West)',
    'S118': 'City (Dhoby Ghaut)',
    'S119': 'Kallang',
    'S120': 'Tanglin',
    'S123': 'Novena',
    'S31': 'Bukit Merah',
    'S46': 'Bukit Timah (East)',
    'S50': 'Bukit Timah',
    'S60': 'Sentosa',
    'S71': 'Queenstown',
    'S72': 'City (Tanjong Pagar)',
    'S77': 'Queenstown (East)',
    'S79': 'City (Somerset)',
    'S90': 'Tanglin (North)',
    'S92': 'Queenstown (South)'
}

rain_data = {
    "S77": 0.0,
    "S120": 0.0,
    "S92": 0.0,
    "S90": 0.0,
    "S79": 0.0,
    "S31": 0.0,
    "S71": 0.0,
    "S111": 0.0,
    "S118": 0.0,
    "S72": 0.0,
    "S46": 0.0,
    "S60": 0.0,
    "S50": 0.0,
    "S07": 0.0,
    "S119": 0.0,
    "S123": 0.0,
    "S116": 0.0,
}

raining_area = []

def time_converter(time):
    try:
     valid_start_converter = datetime.strptime(str(time), '%Y-%m-%d %H:%M:%S')
     valid_start = datetime.strftime(valid_start_converter, '%I:%M%p')

     return valid_start
     
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

def rain_classifier(mm):

    if float(mm) < 0.2:
        a = "Light Rain"
    elif float(mm) < 0.625:
        a = "Moderate Rain"
    elif float(mm) < 4.15:
        a = "Heavy Rain"
    elif float(mm) >= 4.15:
        a = "Violent Rain"

    return a

def send_rain_areas(data):
    global send_rain_message
    global prev_rain_time
    global raining

    no_rain_area = 0
    raining_area.clear()
    counter = 0
    for items in rain_data:
        if counter == 0:
            observation_time = time_converter(data['data']['station'][items]['recorded_date'])
            counter += 1

        current = rain_data[items]
        past = prev_rain_data[items]
        difference = round(float(current) - float(past), 4)
        if difference > 0:
            raining_area.append(items + " " + str(difference))
            no_rain_area += 1

    if no_rain_area > 0:
        prev_rain_time = observation_time
        raining = True
        temp = []
        for items in raining_area:
            temp.append(station_name[items.split(' ')[0]] + " (" + items.split(' ')[1] + "mm, " + rain_classifier(items.split(' ')[1]) + ", " + distance[items.split(' ')[0]] + ")")
        updater.bot.send_message(chat_id='945286667',text = "For the past 5 min before " + observation_time + ", rain was detected at \n- " + "\n- ".join(temp))
        print("For the past 5 min before " + observation_time + ", rain was detected at \n- " + "\n- ".join(temp))

def send(message, time):
    url = config.discord_webhooks
    obj = {"embeds": [{"title": "Heavy Rain Warning","url": "http://www.weather.gov.sg/warning-heavy-rain/","color": 16715535,"fields": [ {"name": "Message", "value": "\n\n".join(message)}], "author": {"name": "Meteorological Service Singapore (MSS)", "url": "http://www.weather.gov.sg/home"}, "footer": {"text": "Issued at"}, "timestamp": time, "thumbnail": {"url": "http://www.weather.gov.sg/wp-content/themes/wiptheme/assets/img/mss-logo.png"}}],"username": "Bot" }

    for items in url:
        requests.post(items, json=obj)

def Check_Both():
    global prev_observation_time
    global send_bad_fore
    global prev_rain_time
    global raining
    global weather_alerts

    try:
        counter = 0
        a = requests.get("http://www.weather.gov.sg/mobile/json/rest-get-latest-observation-for-all-locs.json", timeout=10).json()
        for items in a['data']['station']:
            if str(items) in wanted:
                rain_data.update({str(items): a['data']['station'][str(items)]['rain_mm']})

        for items in rain_data:
            if counter == 0:
                raintime = time_converter(a['data']['station'][items]['recorded_date'])
                counter += 1                

        if prev_rain_data != rain_data:
            send_rain_areas(a)
            prev_rain_data.update(rain_data)
        elif prev_rain_data == rain_data and raintime != prev_rain_time and raining == True:
            updater.bot.send_message(chat_id='945286667',text="No rain has been detected in the past 5 minutes before " + raintime )
            print("No rain has been detected in the past 5 minutes before " + raintime)
            raining = False
            
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    try:
        b = requests.get("http://www.weather.gov.sg/mobile/json/rest-get-all-latest-nowcast.json", timeout=10).json()
        if prev_observation_time != b['data']['nowcastValidStartTime']:
            prev_observation_time = b['data']['nowcastValidStartTime']
            for items in b['data']['nowcastLocations']:
                if items['location'] == "3291":
                    if weathersymbols[items['weather']].split()[-1] == "s":
                        aa = " are expected from "
                    else:
                        aa = " is expected from "
                    if items['weather'] in bad_fore:
                        updater.bot.send_message(chat_id='945286667',text = weathersymbols[items['weather']] + aa + b['data']['nowcastValidStartTime'])
                        send_bad_fore = True
                    elif send_bad_fore == True:
                        updater.bot.send_message(chat_id='945286667',text = weathersymbols[items['weather']] + aa + b['data']['nowcastValidStartTime'])
                        send_bad_fore = False
    except:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

    try:
        c = requests.get("http://www.weather.gov.sg/wp-content/themes/wiptheme/page-functions/functions-ajax-warningbar.php", timeout=10).json()
        be = []
        for items in c:
            for item2 in items['warnings']:
                be.append(item2['title'].replace('<br>', '\n'))
                be.append("Issued at " + item2['issueTime'] + " " + item2['issueDate'])
            for item3 in items['advs']:
                be.append(item3)

        bc = []
        if be != weather_alerts:
            updater.bot.send_message(chat_id='945286667', text="".join(be), disable_web_page_preview=True)
            weather_alerts = be
            print("".join(weather_alerts))

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
    Check_Both()
    time.sleep(30)