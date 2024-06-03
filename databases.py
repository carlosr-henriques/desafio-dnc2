import sqlite3

con = sqlite3.connect("desafio_escola_dnc.db")
cur = con.cursor()

cur.execute("""create table tbl_weather(
    weather_id integer primary key autoincrement,
    date_now text not null,
    city text not null,
    country text not null,
    latitude text not null,
    longitude text not null,
    temp_predicted real not null,
    temp_feels_like_predicted real not null,
    temp_max_predicted real not null,
    temp_min_predicted real not null,
    humidity real not null,
    wind_speed real not null,
    cloudiness real not null,
    description text not null,
    sunset_utc text not null
);""")


cur.execute("""create table tbl_directions(
    weather_id integer primary key,
    start_address text not null,
    end_address text not null,
    distance real not null,
    duration text not null,
    duration_in_traffic text not null,
    start_location_latitude text not null,
    start_location_longitude text not null,
    end_location_latitude text not null,
    end_location_longitude text not null,
    foreign key (weather_id) references tbl_weather(id)
);""")

cur.execute("drop table tb_weather")
cur.execute("drop table tbl_directions")

