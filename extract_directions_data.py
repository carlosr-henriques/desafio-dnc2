from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import googlemaps
import gmaps
import os

load_dotenv(find_dotenv())

con = sqlite3.connect("desafio_escola_dnc.db")
engine = create_engine('sqlite:///desafio_escola_dnc.db', echo=False)

google_maps = googlemaps.Client(key=os.getenv("GOOGLEMAPS_API_KEY"))

def create_directions_index(df):

    conn = sqlite3.connect("desafio_escola_dnc.db")
    query = "SELECT COUNT(*) FROM tbl_direction;"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    conn.close()
   
    df['weather_id'] = pd.to_datetime(df['weather_id'])
    df['weather_id'] = df['weather_id'].dt.strftime('%Y%m%d') + '0' + str(rows[0][0])
    return df

def get_directions(origin, destination, mode, client=google_maps):
    now = datetime.now()
    directions_result = client.directions(origin=origin,
                                        destination=destination,
                                        mode=mode,
                                        departure_time=now)
    
    return {
        "weather_id": [datetime.now().strftime("%Y-%m-%d")],
        "dat_dt_local": [datetime.now().strftime("%Y-%m-%d")],
        "start_address":[directions_result[0]["legs"][0]["start_address"]],
        "end_address": [directions_result[0]["legs"][0]["end_address"]],
        "distance": [directions_result[0]["legs"][0]["distance"]["text"]],
        "duration": [directions_result[0]["legs"][0]["duration"]["text"]],
        "duration_in_traffic": [directions_result[0]["legs"][0]["duration_in_traffic"]["text"]],
        "start_location_latitude": [directions_result[0]["legs"][0]["start_location"]["lat"]],
        "start_location_longitude": [directions_result[0]["legs"][0]["start_location"]["lng"]],
        "end_location_latitude": [directions_result[0]["legs"][0]["end_location"]["lat"]],
        "end_location_longitude": [directions_result[0]["legs"][0]["end_location"]["lng"]]

    }
def get_gmaps(origin: tuple, destination: tuple, client=os.getenv("GOOGLEMAPS_API_KEY")):
    gmaps.configure(api_key=client)
    fig = gmaps.figure()
    origin_to_destination = gmaps.directions_layer(origin, destination)
    fig.add_layer(origin_to_destination)
    return fig

def inser_direction_data(df):
    df.to_sql("tbl_direction", con = engine, if_exists = "append", index = False)

if __name__ == "__main__":

    directions = get_directions(origin="R Caraiba, 441 - Colégio", destination="Av das Américas, 7777", mode="driving")
    df = pd.DataFrame(directions)
    df = create_directions_index(df)
    inser_direction_data(df)