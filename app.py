from extract_weather_data import get_coordinates, get_weather, unity_transform, create_weather_index, insert_weather_data
from extract_directions_data import get_directions, get_gmaps
from geopy.geocoders import Nominatim
import streamlit as st
import pandas as pd
import sqlite3

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

    weather_city_text = st.text_area("Dados de clima", "Insira a cidade")
    weather_country_text = st.text_area("Dados do país", "Insira o país")
    directions_origin_text = st.text_area("Dados da rota", "Insira a origem da rota")
    directions_destination_text = st.text_area("Dado da rota", "Insira o destino da rota")
    directions_mode_selectbox = st.selectbox("Escolha o modo de viagem",
                                            ("Dirigindo", "Andando", "Ciclismo", "Trânsito")
                                            )
    st.button("Confirmar", type="primary")
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
            try:
                coordinates = get_coordinates(weather_city_text, weather_country_text)

                df = pd.DataFrame(coordinates)
                
                df = create_weather_index(df)

                df_weather = df.apply(lambda x: get_weather(x), axis=1)
                df = pd.concat([df, pd.json_normalize(df_weather)], axis=1)

                df = unity_transform(df)

                insert_weather_data(df)

                if directions_mode_selectbox == "Dirigindo":
                    directions_mode_selectbox = "driving"
                elif directions_mode_selectbox == "Andando":
                    directions_mode_selectbox = "walking"
                elif directions_mode_selectbox == "Ciclismo":
                    directions_mode_selectbox = "bicycling"
                else:
                    directions_mode_selectbox = "Transit"

                directions = get_directions(directions_origin_text, directions_destination_text, directions_mode_selectbox)
                st.write("Direções:")
                st.write(directions)
            except Exception as e:
                st.error(f"Erro ao obter direções: {e}")


