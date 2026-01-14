import os
import sys
import time
import datetime
from pathlib import Path

import requests
import psycopg2
import pandas as pd

from io import StringIO
from dotenv import load_dotenv
import pytz

import django
from django.db import connection

# Setup Django
project_root = Path(__file__).resolve().parent.parent / 'mysite'
sys.path.insert(0, str(project_root))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from weather.models import WeatherServices, Locations

#don't know why the WSGI file isn't working but whatever
project_folder = os.path.expanduser('~/mysite/.env')
load_dotenv(project_folder)

weatherapicom_apikey = os.environ.get('WEATHERCOM_KEY')
openweathermap_apikey = os.environ.get('OPENWEATHERMAP_KEY')
visualcrossing_apikey = os.environ.get('VISUALCROSSING_KEY')
tomorrowio_apikey = os.environ.get('TOMORROWIO_KEY')

sqldbname = os.environ.get('SQLDBNAME')
sqlhost = os.environ.get('SQLHOST')
sqluser = os.environ.get('SQLUSER')
sqlpassword = os.environ.get('SQLPASSWORD')
sqlport = os.environ.get('SQLPORT')

# 1 = send to test forecast table
DEBUG = 0

days = 4

current_time = round((int(time.time())) / 3600) * 3600

def getlocations():
    locations = list(Locations.objects.values())
    return locations
    connection.close()

def getservices():
    services = WeatherServices.objects.values()
    connection.close()
    return services

def weathercomcollect(city_id, city, statecode, latitude, longitude, days):
    api_url = f"http://api.weatherapi.com/v1/forecast.json?key={weatherapicom_apikey}&q={latitude},{longitude}&days={days}&aqi=no&alerts=no"

    response = requests.get(api_url, timeout=10)
    data = response.json()
    responsecode = response.status_code

    #print("API url is: " + api_url)
    #print("Reponse code is " + str(responsecode))

    forecasts = []

    for forecastday in data['forecast']['forecastday']:
        for hour in forecastday['hour']:
            forecast = {
                'api_name': "weathercom",
                'city_id': city_id,
                'city': f"{city}, {statecode}",
                'forecast_made': current_time,
                'forecast_epoch': hour['time_epoch'],
                'temp_f': hour['temp_f'],
                'condition': hour['condition']['text'],
                'precip_in': hour['precip_in'],
                'feelslike_f': hour['feelslike_f'],
                'will_it_rain': hour['will_it_rain'],
                'chance_of_rain': hour['chance_of_rain'],
                'chance_of_snow': hour['chance_of_snow']
            }
            forecasts.append(forecast)

    df = pd.DataFrame(forecasts)
    return df

def visualcrossingcollect(city_id, city, statecode, latitude, longitude, days):
    api_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{latitude}%2C%20{longitude}?unitGroup=us&elements=datetime%2CdatetimeEpoch%2Cname%2Csnow%2Clatitude%2Clongitude%2Ctemp%2Cfeelslike%2Cprecip%2Cprecipprob%2Cpreciptype%2Cconditions&include=hours%2Cfcst&key={visualcrossing_apikey}&contentType=json"
    response = requests.get(api_url, timeout=10)
    data = response.json()
    responsecode = response.status_code

    #print("API url is: " + api_url)
    #print("Reponse code is " + str(responsecode))

    forecasts = []

    for forecastday in data['days']:
        for hour in forecastday['hours']:
            preciptype = hour.get('preciptype', [])
            preciptype_str = ','.join(preciptype) if preciptype else ''

            forecast = {
                'api_name': "visualcrossing",
                'city_id': city_id,
                'city': f"{city}, {statecode}",
                'forecast_made': current_time,
                'forecast_epoch': hour['datetimeEpoch'],
                'temp_f': hour['temp'],
                'condition': hour['conditions'],
                'precip_in': hour['precip'],
                'precip_prob': hour['precipprob'],
                'feelslike_f': hour['feelslike'],
                'snow_in': hour['snow'],
                'precip_type': preciptype_str,
            }
            forecasts.append(forecast)

    df = pd.DataFrame(forecasts)
    return df

def tomorrowiocollect(city_id, city, statecode, latitude, longitude, days):
    #https://docs.tomorrow.io/reference/weather-forecast
    #the api should be returning a precipitation type but it's not

    api_url = f"https://api.tomorrow.io/v4/weather/forecast?location={latitude},{longitude}&timesteps=1h&units=imperial&apikey={tomorrowio_apikey}"
    response = requests.get(api_url, timeout=10)
    data = response.json()
    responsecode = response.status_code

    #print("API url is: " + api_url)
    #print("Reponse code is " + str(responsecode))

    forecasts = []

    for hour in data['timelines']['hourly']:
        forecast_time = datetime.datetime.strptime(hour['time'], '%Y-%m-%dT%H:%M:%SZ')
        forecast_time = forecast_time.replace(tzinfo=pytz.UTC)
        epoch_time = int(forecast_time.timestamp())

        forecast = {
            'api_name': "tomorrowio",
            'city_id': city_id,
            'city': f"{city}, {statecode}",
            'forecast_made': current_time,
            'forecast_epoch': epoch_time,
            'temp_f': hour['values']['temperature'],
            'feelslike_f': hour['values']['temperatureApparent'],
            'condition': hour['values']['weatherCode'],
            'snow_in': hour['values']['snowAccumulation'],
            'rain_in': hour['values']['rainAccumulation'],
#           'sleet_in': hour['values']['sleetAccumulation'], - API is not returning this right now. Not sure why.
            'precip_prob': hour['values']['precipitationProbability'],
        }
        forecasts.append(forecast)

    df = pd.DataFrame(forecasts)
    return df

def openmeteocollect(city_id, city, statecode, latitude, longitude, days):
    #https://open-meteo.com/en/docs
    #no api key needed, 14 day forecast

    api_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,apparent_temperature,precipitation_probability,precipitation,rain,snowfall&timezone=GMT&temperature_unit=fahrenheit&precipitation_unit=inch&forecast_days={days}"
    response = requests.get(api_url, timeout=10)
    data = response.json()
    responsecode = response.status_code
    #print("API url is: " + api_url)
    #print("Reponse code is " + str(responsecode))
    #print(" ")


    time_list = data['hourly']['time']
    temperature_list = data['hourly']['temperature_2m']
    apparent_temperature_list = data['hourly']['apparent_temperature']
    precip_prob_list = data['hourly']['precipitation_probability']
    precipitation_list = data['hourly']['precipitation']
    rain_list = data['hourly']['rain']
    snowfall_list = data['hourly']['snowfall']

    epoch_time_list = []
    for timestamp in time_list:
        dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M")
        dt = dt.replace(tzinfo=pytz.UTC)
        epoch_time = int(dt.timestamp())
        epoch_time_list.append(epoch_time)

    dfdata = {
        'api_name': "openmeteo",
        'city_id': city_id,
        'city': f"{city}, {statecode}",
        'forecast_made': current_time,
        'forecast_epoch' : epoch_time_list,
        'temp_f' : temperature_list,
        'feelslike_f' : apparent_temperature_list,
        'precip_prob' : precip_prob_list,
        'precip_in' : precipitation_list,
        'rain_in' : rain_list,
        'snow_in' : snowfall_list
    }

    df = pd.DataFrame(dfdata)
    return(df)

#https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
def dbsend(forecastframe):

    #connect to database and execute
    conn = psycopg2.connect(dbname = sqldbname,
                    host = sqlhost,
                    user = sqluser,
                    password = sqlpassword,
                    port = sqlport)

    buffer = StringIO()
    forecastframe.to_csv(buffer, index=False, header=True)
    buffer.seek(0)

    cursor = conn.cursor()
    try:
        if DEBUG == 0:
            cursor.copy_expert("COPY weather_forecastdata(api_name, city_id, city, forecast_made, forecast_epoch, temp_f, condition, precip_in, feelslike_f, will_it_rain, chance_of_rain, chance_of_snow, precip_prob, snow_in, precip_type, rain_in, sleet_in) FROM STDIN WITH CSV HEADER", buffer)
        elif DEBUG == 1:
            cursor.copy_expert("COPY weather_testforecastdata(api_name, city_id, city, forecast_made, forecast_epoch, temp_f, condition, precip_in, feelslike_f, will_it_rain, chance_of_rain, chance_of_snow, precip_prob, snow_in, precip_type, rain_in, sleet_in) FROM STDIN WITH CSV HEADER", buffer)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1

    print("forecast copied to database.")
    cursor.close()
    connection.close()


def collectweather(locationlist):
    services = getservices()
    all_forecasts = []

    for index, city_info in enumerate(locationlist, start=1):
        city_id = city_info['city_id']
        city = city_info['city_name']
        statecode = city_info['state_code']
        latitude = city_info['latitude']
        longitude = city_info['longitude']

        for service in services:
            api_name = service['api_ref_name']

            if index > service['hourly_api_limit']:
                print(f"Hourly API limit reached for {api_name}.")
                continue

            collect_function = globals().get(service['api_ref_name'] + "collect")

            if collect_function:
                try:
                    forecast = collect_function(city_id, city, statecode, latitude, longitude, days)
                    all_forecasts.append(forecast)
                except Exception as error:
                    print(f"Unable to get forecast from {api_name} at {city}, {statecode} with error message:", error)

    combined_forecast = pd.concat(all_forecasts, ignore_index=True)

    #this used to be handled at the individual API levels but services kept adding "forecasts" for hours prior to when the forecast was made so doing this globally now.
    epoch_mask = combined_forecast['forecast_made'] > combined_forecast['forecast_epoch']
    combined_forecast = combined_forecast[~epoch_mask]

    # this ensures all required columns exist before sending to the db. If this isn't done one weather service failing will prevent it being sent
    required_columns = [
        'api_name', 'city_id', 'city', 'forecast_made', 'forecast_epoch', 'temp_f', 'condition',
        'precip_in', 'feelslike_f', 'will_it_rain', 'chance_of_rain', 'chance_of_snow',
        'precip_prob', 'snow_in', 'precip_type', 'rain_in', 'sleet_in'
    ]

    for column in required_columns:
        if column not in combined_forecast.columns:
            combined_forecast[column] = pd.NA

    combined_forecast = combined_forecast[required_columns]
    dbsend(combined_forecast)


def main():
    locations = getlocations()
    collectweather(locations)

if __name__ == "__main__":
    main()