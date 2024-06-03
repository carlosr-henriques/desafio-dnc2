from extract_weather_data import get_coordinates, get_weather, unity_transform, create_weather_index, insert_weather_data, utc_transform
from extract_directions_data import get_directions, get_gmaps, create_directions_index, inser_direction_data
from folium import FeatureGroup, LayerControl
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import streamlit as st
import pandas as pd
import sqlite3
import json
import folium


def get_weather_data_from_db(db_path):
    # Conectar ao banco de dados
    conn = sqlite3.connect("desafio_escola_dnc.db")
    query = "SELECT * FROM tbl_weather;"
    df_weather = pd.read_sql_query(query, conn)
    conn.close()
    
    return df_weather

def verifica_cidade(lat, long, cidade, pais):
    geolocator = Nominatim(user_agent="DesafioEscolaDNC")
    location = geolocator.reverse((lat, long))
    address = location.raw['address']
    
    if cidade.lower() in address.get('city', '').lower() and pais.lower() in address.get('country', '').lower():
        return True
    else:
        return False

check = st.checkbox("Checar dados histórico")

if check:
    df = get_weather_data_from_db("desafio_escola_dnc")
    directions_mode_selectbox = st.selectbox("Escolha o modo de viagem",
                                            (list(df.itertuples(index=False)))
                                            )
else:

    weather_city_text = st.text_area("Dados de clima")
    weather_country_text = st.text_area("Dados do país")
    directions_origin_text = st.text_area("Dados da rota")
    directions_destination_text = st.text_area("Dado da rota")
    directions_mode_selectbox = st.selectbox("Escolha o modo de viagem",
                                            ("Dirigindo", "Andando", "Ciclismo", "Trânsito")
                                            )
    if st.button("Confirmar", type="primary"):
        if not weather_city_text:
            st.error("O campo 'Dados de clima - Cidade' está vazio.")
        elif not weather_country_text:
            st.error("O campo 'Dados de clima - País' está vazio.")
        elif not directions_origin_text:
            st.error("O campo 'Dados da rota - Origem' está vazio.")
        elif not directions_destination_text:
            st.error("O campo 'Dados da rota - Destino' está vazio.")
        else:
            # Se todos os campos estiverem preenchidos, execute a lógica desejada
            st.success("Todos os campos foram preenchidos corretamente.")
            coordinates = get_coordinates(weather_city_text, weather_country_text)

            df = pd.DataFrame(coordinates)
            
            df_weather = df.apply(lambda x: get_weather(x), axis=1)
            
            df_weather = pd.concat([df, pd.json_normalize(df_weather)], axis=1)

            df = create_weather_index(df_weather)

            df_weather = unity_transform(df_weather)
            
            df_weather = utc_transform(df_weather)

            insert_weather_data(df_weather)

            if directions_mode_selectbox == "Dirigindo":
                directions_mode_selectbox = "driving"
            elif directions_mode_selectbox == "Andando":
                directions_mode_selectbox = "walking"
            elif directions_mode_selectbox == "Ciclismo":
                directions_mode_selectbox = "bicycling"
            else:
                directions_mode_selectbox = "transit"

            directions = get_directions(directions_origin_text, directions_destination_text, directions_mode_selectbox)

            df_directions = pd.DataFrame(directions)

            df_directions = create_directions_index(df_directions)

            inser_direction_data(df_directions)
            
           

            json_weather = df_weather.to_json(orient="index")
            json_weather = json.loads(json_weather)

            st.metric("Cidade", json_weather["0"]["city"])

            col1, col2, col3= st.columns(3)

            col1.metric("Temperatura prevista", json_weather["0"]["temp_predicted"])
            col2.metric("Temperatura mínima", json_weather["0"]["temp_min_predicted"])
            col3.metric("Temperatura máxima", json_weather["0"]["temp_max_predicted"])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Sensação térmica", json_weather["0"]["temp_feels_like_predicted"])
            col2.metric("Umidade", f"{json_weather['0']['humidity']*100}%")
            col3.metric("Velocidade do vento", f"{json_weather['0']['wind_speed']}%")
            col4.metric("Situação", json_weather["0"]["description"].capitalize())

            json_directions = df_directions.to_json(orient="index")
            json_directions = json.loads(json_directions)

            col1, col2, col3 = st.columns(3)
            col1.metric("Distância", json_directions["0"]["distance"])
            col2.metric("Duração", json_directions["0"]["duration"])
            col3.metric("Duração no trânsito", json_directions["0"]["duration_in_traffic"])

            #fig = get_gmaps(origin=(directions["start_location_latitude"][0], directions["start_location_longitude"][0]), destination=(directions["end_location_latitude"][0], directions["end_location_longitude"][0]))

            origin = [directions["start_location_latitude"][0], directions["start_location_longitude"][0]]
            destination = [directions["end_location_latitude"][0], directions["end_location_longitude"][0]]
            

            m = folium.Map(location=origin, zoom_start=10)
    
            # Adicionar marcadores para as duas localizações
            folium.Marker(location=origin, popup='Location 1').add_to(m)
            folium.Marker(location=destination, popup='Location 2').add_to(m)
            folium.PolyLine(locations=[origin, destination], color='blue').add_to(m)
            
            # Traçar uma linha entre as duas localizações
            st_folium(m, width=725)

                        


