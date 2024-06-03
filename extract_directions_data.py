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
engine = create_engine('sqlite:///database/desafio_escola_dnc.db', echo=False)

google_maps = googlemaps.Client(key=os.getenv("GOOGLEMAPS_API_KEY"))

def get_directions(origin, destination, mode, client=google_maps):
    now = datetime.now()
    directions_result = client.directions(origin=origin,
                                        destination=destination,
                                        mode=mode,
                                        departure_time=now)
    
    return {
        "start_address":directions_result[0]["legs"][0]["start_address"],
        "end_address":directions_result[0]["legs"][0]["end_address"],
        "distance":directions_result[0]["legs"][0]["distance"]["text"],
        "duration":directions_result[0]["legs"][0]["duration"]["text"],
        "duration_in_traffic":directions_result[0]["legs"][0]["duration_in_traffic"]["text"],
        "start_location_latitude":directions_result[0]["legs"][0]["start_location"]["lat"],
        "start_location_longitude":directions_result[0]["legs"][0]["start_location"]["lng"],
        "end_location_latitude":directions_result[0]["legs"][0]["start_location"]["lat"],
        "end_location_longitude":directions_result[0]["legs"][0]["start_location"]["lng"]

    }
def get_gmaps(client, origin: tuple, destination: tuple):
    gmaps.configure(api_key=os.getenv("GOOGLEMAPS_API_KEY"))
    fig = gmaps.figure()
    origin_to_destination = gmaps.directions_layer(origin, destination)
    fig.add_layer(origin_to_destination)
    return fig

def inser_direction_data(df):
    df.to_sql("tbl_directions", con = engine, if_exists = "append", index = False)
    con.close()
