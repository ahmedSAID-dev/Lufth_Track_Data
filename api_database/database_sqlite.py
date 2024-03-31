import json
import sqlite3

def get_aircraft_information(aircraft_code: str) -> dict:
    conn = sqlite3.connect("lufth_track_data.db")
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM aircraft
        WHERE aircraft_code = ?
    """, (aircraft_code,))

    result = c.fetchone()
    conn.close()

    if result is None:
        return None

    return {
        "aircraft_code": result[0],
        "name": result[1],
    }

def get_airport_information(airport_code: str) -> dict:
    conn = sqlite3.connect("lufth_track_data.db")
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM airport
        WHERE airport_code = ?
    """, (airport_code,))

    result = c.fetchone()
    conn.close()

    if result is None:
        return None

    return {
        "airport_code": result[0],
        "latitude": result[1],
        "longitude": result[2],
        "city_code": result[3],
        "country_code": result[4],
        "timezone_id": result[5],
        "utc_offset": result[6],
    }

def get_airline_information(airline_id: str) -> dict:
    conn = sqlite3.connect("lufth_track_data.db")
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM airline
        WHERE airline_id = ?
    """, (airline_id,))

    result = c.fetchone()
    conn.close()

    if result is None:
        return None

    return {
        "airline_id": result[0],
        "airline_id_icao": result[1],
        "name": result[2],
    }

def update_airports():
    # Chargement des données JSON
    with open("../data_fixe/airports.json", "r") as f:
        data = json.load(f)
        airport_data = data
        # mon json est nettoyé ici
        # airport_data = data["AirportResource"]["Airports"]["Airport"]

    # Suppression de l'ancienne table
    conn = sqlite3.connect("lufth_track_data.db")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS airport")

    # Création de la nouvelle table
    c.execute("""
        CREATE TABLE airport (
            airport_code TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL,
            city_code TEXT,
            country_code TEXT,
            timezone_id TEXT,
            utc_offset TEXT
        )
    """)

    # Insertion des données
    for airport in airport_data:
        airport_code = airport["AirportCode"]
        latitude = airport["Position"]["Coordinate"]["Latitude"]
        longitude = airport["Position"]["Coordinate"]["Longitude"]
        city_code = airport["CityCode"]
        country_code = airport["CountryCode"]
        utc_offset = airport["UtcOffset"]
        c.execute("""
            INSERT INTO airport (
                airport_code,
                latitude,
                longitude,
                city_code,
                country_code,
                utc_offset
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (airport_code, latitude, longitude, city_code, country_code, utc_offset))

    # Enregistrement et fermeture de la connexion
    conn.commit()
    conn.close()

    # Retour du nombre d'aéroports
    return len(airport_data)

def update_aircrafts():

  # Chargement des données JSON
  with open("../data_fixe/aircrafts.json", "r") as f:
    data = json.load(f)
    aircraft_data = data
    # aircraft_data = data["AircraftResource"]["AircraftSummaries"]["AircraftSummary"]

  # Suppression de l'ancienne table
  conn = sqlite3.connect("lufth_track_data.db")
  c = conn.cursor()
  c.execute("DROP TABLE IF EXISTS aircraft")

  # Création de la nouvelle table (modifiée)
  c.execute("""
    CREATE TABLE aircraft (
      aircraft_code TEXT PRIMARY KEY,
      name TEXT
    )
  """)

  # Insertion des données (modifiée)
  for aircraft in aircraft_data:
    aircraft_code = aircraft["AircraftCode"]
    name = aircraft["Names"]["Name"]["$"]
    
    c.execute("""
      INSERT OR IGNORE INTO aircraft (
        aircraft_code,
        name
      )
      VALUES (?, ?)
    """, (aircraft_code, name))

  # Enregistrement et fermeture de la connexion
  conn.commit()
  conn.close()

  # Retour du nombre d'avions
  return len(aircraft_data)


def update_airlines():

  # Chargement des données JSON
  with open("../data_fixe/airlines.json", "r") as f:
    data = json.load(f)
    airline_data = data
    # airline_data = data["AirlineResource"]["Airlines"]["Airline"]

  # Suppression de l'ancienne table
  conn = sqlite3.connect("lufth_track_data.db")
  c = conn.cursor()
  c.execute("DROP TABLE IF EXISTS airline")

  # Création de la nouvelle table (modified)
  c.execute("""
    CREATE TABLE airline (
      airline_id TEXT PRIMARY KEY,
      airline_id_icao,
      name TEXT
    )
  """)

  # Insertion des données (modified)
  for airline in airline_data:
    airline_id = airline["AirlineID"]
    airline_id_icao = airline.get("AirlineID_ICAO", "")
    # Extract name from nested "Names" dictionary
    name = airline["Names"]["Name"]["$"]
    # print(airline_id)
    c.execute("""
      INSERT OR IGNORE INTO airline (
        airline_id,
        airline_id_icao,
        name
      )
      VALUES (?, ?, ?)
    """, (airline_id, airline_id_icao, name))

  # Enregistrement et fermeture de la connexion
  conn.commit()
  conn.close()

  # Retour du nombre de compagnies aériennes
  return len(airline_data)


