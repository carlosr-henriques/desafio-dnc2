from geopy.extra.rate_limiter import RateLimiter
from dotenv import load_dotenv, find_dotenv
from geopy.geocoders import Nominatim
from sqlalchemy import create_engine
from pytz import timezone
import pandas as pd
import timezonefinder
import sqlite3
import requests
import datetime
from datetime import datetime
import os

load_dotenv(find_dotenv())

con = sqlite3.connect("desafio_escola_dnc.db")
cur = con.cursor()

engine = create_engine('sqlite:///desafio_escola_dnc.db', echo=False)

LANG = "pt_br"
openweather_api = os.getenv("OPENWEATHER_API_KEY")

def get_coordinates(city, country):
    locator = Nominatim(user_agent="DesafioEscolaDNC")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=.1)
    response = geocode(query={"city": city, "country": country})
    return {
        "city":[city], "country": [country],
        "latitude":[response.latitude], "longitude":[response.longitude]
        }
# Corrigir conversao utc
def get_weather(df):
    
    """Pass the DataFrame contains city, country, latitude and longitute. This informations will be get in API."""
    
    URL = f"https://api.openweathermap.org/data/2.5/weather?lat={df['latitude']}&lon={df['longitude']}&appid={openweather_api}&lang={LANG}"
    response = requests.get(URL)
    response_json = response.json()
    return {
      "date_now":datetime.now(),
      "temp_predicted": response_json["main"]["temp"] - 273.15,
      "temp_feels_like_predicted": response_json["main"]["feels_like"] - 273.15,
      "temp_max_predicted": response_json["main"]["temp_max"] - 273.15,
      "temp_min_predicted": response_json["main"]["temp_min"] - 273.15,
      "humidity": response_json["main"]["humidity"],
      "wind_speed": response_json["wind"]["speed"],
      "cloudiness": response_json["clouds"]["all"],
      "description": response_json["weather"][0]["description"],
      "sunset_utc": response_json["sys"]["sunset"]
    }

def insert_weather_data(df):
    df.to_sql("tbl_weather", con = engine, if_exists = "append", index = False)

def unity_transform(df):

    df["humidity"] = df["humidity"]/100
    df["cloudiness"] = df["cloudiness"]/100

    return df

def create_weather_index(df):

    conn = sqlite3.connect("desafio_escola_dnc.db")
    query = "SELECT COUNT(*) FROM tbl_weather;"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    conn.close()
   
    df['date_now'] = pd.to_datetime(df['date_now'])
    df['date_now'] = df['date_now'].dt.strftime('%Y%m%d') + '0'+ str(rows[0][0])
    return df

def utc_transform(df):
    
    tf = timezonefinder.TimezoneFinder()

    # Função auxiliar para converter timestamp UTC para hora local
    def get_local_time(df):
        
        lat = df['latitude']
        lon = df['longitude']
        timestamp = df['sunset_utc']

        # Obter o fuso horário para a localização
        timezone_name = tf.certain_timezone_at(lat=lat, lng=lon)
        
        if timezone_name:
            local_time = datetime.fromtimestamp(timestamp, tz = timezone(timezone_name))
            return local_time.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return None

        # Aplicar a função auxiliar ao DataFrame
    df["local_time"] = df.apply(get_local_time, axis=1)

    return df

if __name__ == "__main__":

    coordinates = get_coordinates("Rio de Janeiro", "Brazil")

    df = pd.DataFrame(coordinates)

    df_weather = df.apply(lambda x: get_weather(x), axis=1)
    df = pd.concat([df, pd.json_normalize(df_weather)], axis=1)

    df = create_weather_index(df)

    df = unity_transform(df)

    insert_weather_data(df)


