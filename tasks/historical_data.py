import os
import sys
import time
from pathlib import Path

import requests

import django
from django.db import connection

project_root = Path(__file__).resolve().parent.parent / 'mysite'
sys.path.insert(0, str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

# flake8: noqa: E402
from weather.models import Locations, HistoricalData

google_apikey = os.environ.get('GOOGLE_KEY')

def getlocations():
    locations = list(Locations.objects.values())
    connection.close()
    return locations

last_hour_time = (round((int(time.time())) // 3600) * 3600) - 3600 #Subtract 3600 to get previous hours epoch


def googlecollect(city_id, city_name, statecode, latitude, longitude):
    try:
        api_url = f"https://weather.googleapis.com/v1/history/hours:lookup?key={google_apikey}&location.latitude={latitude}&location.longitude={longitude}&hours=1&unitsSystem=IMPERIAL"

        response = requests.get(api_url)
        data = response.json()
        response_code = response.status_code

        temp_f = data['historyHours'][0]['temperature']['degrees']
        precip_prob = data['historyHours'][0]['precipitation']['probability']['percent']
        precip_in = data['historyHours'][0]['precipitation']['qpf']['quantity']

        HistoricalData.objects.create(city_id=city_id, api_name="google", city_name=city_name, time_epoch=last_hour_time, temp_f=temp_f, precip_in=precip_in, precip_prob=precip_prob)

    except Exception as e:
        print(f"could not collect weather forecast at {city_name}, {statecode}")
        print(f"api url is {api_url}")
        print(f"reponse code is {response_code}")
        print(f"error is {e}")

def main():
    locations = getlocations()
    
    for location in locations:
        googlecollect(location['city_id'], location['city_name'], location['state_code'], location['latitude'], location['longitude'])
    

if __name__ == "__main__":
    main()