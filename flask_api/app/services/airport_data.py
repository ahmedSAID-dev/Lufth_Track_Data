import pandas as pd
import pymongo
from ..utils.caching import cache

client = pymongo.MongoClient("mongodb://mongo_l:27017/")
db = client['lufth_track_data']

@cache.cached(timeout=3600)
def get_airports():
    """
    Récupère les données des aéroports depuis la base de données MongoDB.
    
    Returns:
        list: Une liste de documents d'aéroports.
    """
    airports = list(db['c_airports'].find())
    return airports

@cache.cached(timeout=3600)
def get_airports_df(airports_list, ALL_AIRPORTS=True):
    """
    Récupère les données des aéroports depuis MongoDB et les convertit en DataFrame Pandas.
    
    Returns:
        pd.DataFrame: Un DataFrame contenant les données des aéroports.
    """
    airports = list(db['c_airports'].find())
    
    # Initialiser une liste pour stocker les données des aéroports
    airport_data = []
    
    # Parcourir chaque document d'aéroport
    for airport in airports:
        airport_code = airport['AirportCode']
        # Vérifier si on doit filtrer les aéroports
        if not ALL_AIRPORTS and airport_code not in airports_list:
            continue  # Passer cet aéroport s'il n'est pas dans la liste
        
        latitude = airport['Position']['Coordinate']['Latitude']
        longitude = airport['Position']['Coordinate']['Longitude']
        city_code = airport['CityCode']
        country_code = airport.get('CountryCode', 'Inconnu') 
        airport_name = airport['Names']['Name']['$']
        
        # Ajouter les données de l'aéroport à la liste
        airport_data.append({
            'AirportCode': airport_code,
            'Latitude': latitude,
            'Longitude': longitude,
            'CityCode': city_code,
            'CountryCode': country_code,
            'Name': airport_name
        })
    
    # Convertir la liste en DataFrame
    df_airports = pd.DataFrame(airport_data)
    # airports_df = [{'AirportCode': 'CDG', 'Name': 'Charles de Gaulle', 'CountryCode':'FRA'},
                #    {'AirportCode': 'FRA', 'Name': 'FRANKFURT', 'CountryCode':'ALL'}]
    return df_airports
