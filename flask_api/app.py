from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_caching import Cache
import pymongo
import json
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import logging
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'
cache = Cache(app, config={'CACHE_TYPE': 'simple'})  # Configure Flask-Caching

ALL_AIRPORTS = False
airports_list = ["FRA", "JFK", "MUC", "CDG", "DXB", "LAS", "DOH", "LAX"]
# Connexion à MongoDB
client = pymongo.MongoClient("mongodb://mongo_l:27017/")
db = client['lufth_track_data']

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Classe utilisateur pour Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id
# Création du dossier logs s'il n'existe pas
if not os.path.exists("./logs"):
    os.makedirs("./logs")
# Configuration du logging
log_file = "./logs/flask.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Fonction pour charger l'utilisateur
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Fonction pour récupérer les données de vol et d'aéroport
@cache.cached(timeout=3600)  # Cache les résultats pendant 1 heure (en secondes)
def get_flight_data(departure_airport=None, arrival_airport=None):
    """
    Récupère les données de vols depuis MongoDB et applique des filtres
    en fonction des arguments optionnels.
    Args:
        departure_airport (str, optional): Code de l'aéroport de départ pour filtrer les vols.
            Defaults to None (all departures).
        arrival_airport (str, optional): Code de l'aéroport d'arrivée pour filtrer les vols.
            Defaults to None (all arrivals).

    Returns:
        tuple: Un tuple contenant deux listes:
            - flights (list): List of flight documents.
            - airports (list): List of airport documents.
    """

    filters = []
    # Commande mongo
    # db.c_flights_info.find({"$and": [{"status": /\"Departure\":{\"AirportCode\":\"CDG\"/},{"status": /\"Arrival\":{\"AirportCode\":\"FRA\"/}]}).pretty()

    if departure_airport:

        # Filtre pour l'aéroport de départ
        departure_filter = {
            "status": re.compile(rf'"Departure":{{"AirportCode":"{departure_airport}"')
        }
        filters.append(departure_filter)

    if arrival_airport:
        # Filtre pour l'aéroport d'arrivée
        arrival_filter = {
            "status": re.compile(rf'"Arrival":{{"AirportCode":"{arrival_airport}"')
        }
        filters.append(arrival_filter)

    # Si nous avons des filtres, les combiner avec $and
    if filters:
        combined_filters = {"$and": filters}
    else:
        combined_filters = {}

    print(f"Filters constructed: {combined_filters}")
        # ({"status": /{\"Departure\":{\"AirportCode\":\"CDG\"/})
    # print(f"Filters constructed: {filters}")
    flights = list(db['c_flights_info'].find(combined_filters))
    # print(f"les flights: {flights}")
    airports = list(db['c_airports'].find())
    return flights, airports

@cache.cached(timeout=3600)  # Cache les résultats pendant 1 heure (en secondes)
def get_airports():
    """
    Récupère les données des aéroports depuis la base de données MongoDB.
    
    Returns:
        list: Une liste de documents d'aéroports.
    """
    airports = list(db['c_airports'].find())
    return airports

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
    
    return df_airports

def process_flight_data(flights, airports):
    """
    Traite les données des vols et des aéroports pour préparer les informations nécessaires à la création du graphique.
    
    Args:
        flights (list): Une liste de documents de vols.
        airports (list): Une liste de documents d'aéroports.
    
    Returns:
        pd.DataFrame: Un DataFrame contenant les données de vol traitées.
    """
    flight_data = []
    status_colors = {
        "Flight On Time": "blue",
        "Flight Early": "green",
        "Flight Delayed": "red"
    }
    for flight in flights:
        if 'status' in flight and flight['status']:
            try:
                flight_status = json.loads(flight['status'])
                if 'Flights' in flight_status['FlightStatusResource']:
                    for flight_detail in flight_status['FlightStatusResource']['Flights']['Flight']:
                        origin = next((airport for airport in airports if airport['AirportCode'] == flight_detail['Departure']['AirportCode']), None)
                        destination = next((airport for airport in airports if airport['AirportCode'] == flight_detail['Arrival']['AirportCode']), None)
                        if origin and destination:
                            flight_type = flight['type']
                            time_status = flight_detail['Departure']['TimeStatus']['Definition']
                            flight_number = flight_detail['MarketingCarrier']['FlightNumber']
                            departure_date = flight_detail['Departure']['ScheduledTimeLocal']['DateTime']
                            flight_data.append({
                                'origin_lat': origin['Position']['Coordinate']['Latitude'],
                                'origin_lon': origin['Position']['Coordinate']['Longitude'],
                                'destination_lat': destination['Position']['Coordinate']['Latitude'],
                                'destination_lon': destination['Position']['Coordinate']['Longitude'],
                                'origin_code': origin['AirportCode'],
                                'destination_code': destination['AirportCode'],
                                'airport_name': origin['Names']['Name']['$'],
                                'flight_number': flight_number,
                                'time_status': time_status,
                                'departure_date': departure_date,
                                'color': status_colors.get(time_status, 'black'),
                                'line_type': 'connecting' if flight_type == "connecting flight" else 'single',
                                'hover_text': (
                                    f"Departure: {origin['Names']['Name']['$']} ({origin['AirportCode']})<br>"
                                    f"Arrival: {destination['Names']['Name']['$']} ({destination['AirportCode']})<br>"
                                    f"Flight Number: {flight_number}<br>"
                                    f"Equipment: {flight_detail['Equipment']['AircraftCode']}<br>"
                                    f"Status: {time_status}<br>"
                                    f"Departure Date: {departure_date}"
                                )
                            })
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(flight_data)

# Création du graphique Plotly interactif


# Création du graphique Plotly interactif
def create_plot(flight_df, airports_df):
    """
    Crée un graphique Plotly interactif pour visualiser les vols et les aéroports.
    
    Args:
        flight_df (pd.DataFrame): Un DataFrame contenant les données des vols.
        airports_df (pd.DataFrame): Un DataFrame contenant les données des aéroports.
    
    Returns:
        go.Figure: Une figure Plotly contenant le graphique.
    """
    fig = go.Figure()

    # Créer des traces pour chaque ligne de vol
    for _, row in flight_df.iterrows():
        if row['line_type'] == 'connecting':
            fig.add_trace(go.Scattermapbox(
                lat=[row['origin_lat'], row['destination_lat']],
                lon=[row['origin_lon'], row['destination_lon']],
                mode='lines',
                line=dict(width=2, color=row['color']),
                # line=dict(width=2, color=row['color'], symbol= 'arrow'),
                hoverinfo='text',
                hovertext=row['hover_text'],
                name=f"CONNECTING {row['flight_number']} from {row['origin_code']} to {row['destination_code']}"
            ))
        else:
            fig.add_trace(go.Scattermapbox(
                lat=[row['origin_lat'], row['destination_lat']],
                lon=[row['origin_lon'], row['destination_lon']],
                mode='lines',
                line=dict(width=3, color=row['color']),
                hoverinfo='text',
                hovertext=row['hover_text'],
                name=f"SINGLE {row['flight_number']} from {row['origin_code']} to {row['destination_code']}"
            ))

    # Ajouter les points d'aéroport à la carte
    for _, airport in airports_df.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[airport['Latitude']],
            lon=[airport['Longitude']],
            mode='markers+text',
            marker=dict(size=10, color='black'),
            text=airport['AirportCode'],
            textposition='top center',
            hoverinfo='text',
            hovertext=f"Aéroport: {airport['Name']} ({airport['AirportCode']})",
            name=f"{airport['Name']}"
        ))
    # Ajouter legende satut couleur
    status_colors = {
        "Flight On Time": "blue",
        "Flight Early": "green",
        "Flight Delayed": "red"
    }
    for status, color in status_colors.items():
        fig.add_trace(go.Scattermapbox(
            lat=[None],  # Dummy value
            lon=[None],  # Dummy value
            mode='markers',
            marker=dict(size=10, color=color),
            name=status,
            showlegend=True
        ))
    fig.update_layout(
        title='Flights and Airports',
        mapbox=dict(
            style='open-street-map',
            zoom=2
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig

@app.route('/')
def home():
    return redirect(url_for('login'))

# Route principale de l'application Flask
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Route principale de l'application Flask. Affiche la page d'accueil avec le graphique des vols et des aéroports.
    
    Returns:
        str: Le rendu de la page d'accueil.
    """
    flights, airports = get_flight_data()
    flight_df = process_flight_data(flights, airports)
    airports_df = get_airports_df(airports_list, ALL_AIRPORTS)

    if request.method == 'POST':
        flight_type = request.form['flightType']
        if flight_type == 'single':
            filtered_df = flight_df[flight_df['line_type'] == 'single']
        elif flight_type == 'connecting':
            filtered_df = flight_df[flight_df['line_type'] == 'connecting']
        else:
            filtered_df = flight_df  # Par défaut, affiche tous les vols si aucune sélection n'est faite

        fig = create_plot(filtered_df, airports_df)
        graphJSON = fig.to_json()
        return jsonify(graphJSON=graphJSON)

    fig = create_plot(flight_df, airports_df)
    graphJSON = fig.to_json()
    return render_template('index.html', graphJSON=graphJSON)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simuler une vérification de l'utilisateur
        if username == 'admin' and password == 'password':
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/airport', methods=['GET', 'POST'])
@login_required
def airport():
    """
    Route pour sélectionner les aéroports de départ et d'arrivée et afficher le graphique des vols correspondants.
    
    Returns:
        str: Le rendu de la page avec le formulaire de sélection des aéroports et le graphique.
    """
    airports_ls= get_airports()
    airports_df= get_airports_df(airports_list, ALL_AIRPORTS)
    # airports_df = [{'AirportCode': 'CDG', 'Name': 'Charles de Gaulle', 'CountryCode':'FRA'},
                #    {'AirportCode': 'FRA', 'Name': 'FRANKFURT', 'CountryCode':'ALL'}]
    graphJSON = None
    departure_airport_code = None
    arrival_airport_code = None

    error_message = None

    if request.method == 'POST':
        departure_airport_code = request.form.get('departureAirport')
        arrival_airport_code = request.form.get('arrivalAirport')
        logging.debug(departure_airport_code)
        
        
        if not departure_airport_code and not arrival_airport_code:
            logging.info(f"Relation créée entre {departure_airport_code } et {arrival_airport_code} ")

            # Récupérer les données de vol et les filtrer par les aéroports sélectionnés
            flights, airports = get_flight_data(departure_airport_code,arrival_airport_code)
            flight_df = process_flight_data(flights, airports)


            if not flight_df.empty:
                # Créer le graphique Plotly pour les vols filtrés
                fig = create_plot(flight_df, airports_df)
                graphJSON = fig.to_json()
            else:
                graphJSON = {}  # Ou renvoyer un message d'erreur
        else:
            error_message = "Aéroport non trouvé. Veuillez sélectionner des aéroports valides."

        return jsonify({
            'graphJSON': graphJSON,
            'departureAirportCode': departure_airport_code,
            'arrivalAirportCode': arrival_airport_code
        })

    return render_template('airport.html', airports=airports_ls, graphJSON=graphJSON, error_message=error_message)
# Route principale de l'application Flask
@app.route('/tester', methods=['GET', 'POST'])
@login_required
def tester():
    """
    Route principale de l'application Flask. Affiche la page d'accueil avec le graphique des vols et des aéroports.
    
    Returns:
        str: Le rendu de la page d'accueil.
    """
    graphJSON = None
    # airports_list= get_airports()
    
    airports_list = [
    {
        "AirportCode": "FRA",
        "Position": {
            "Coordinate": {
                "Latitude": 50.0331,
                "Longitude": 8.5706
            }
        },
        "CityCode": "FRA",
        "CountryCode": "DE",
        "LocationType": "Airport",
        "Names": {
            "Name": {
                "@LanguageCode": "en",
                "$": "Frankfurt/Main International"
            }
        },
        "UtcOffset": "2.0",
        "TimeZoneId": "Europe/Berlin"
    },
    {
        "AirportCode": "CDG",
        "Position": {
            "Coordinate": {
                "Latitude": 49.0097,
                "Longitude": 2.5478
            }
        },
        "CityCode": "PAR",
        "CountryCode": "FR",
        "LocationType": "Airport",
        "Names": {
            "Name": {
                "@LanguageCode": "en",
                "$": "Paris - Charles De Gaulle"
            }
        },
        "UtcOffset": "2.0",
        "TimeZoneId": "Europe/Paris"
    },
    {
        "AirportCode": "JFK",
        "Position": {
            "Coordinate": {
                "Latitude": 40.6397,
                "Longitude": -73.7789
            }
        },
        "CityCode": "NYC",
        "CountryCode": "US",
        "LocationType": "Airport",
        "Names": {
            "Name": {
                "@LanguageCode": "en",
                "$": "New York - JFK International, NY"
            }
        },
        "UtcOffset": "-4.0",
        "TimeZoneId": "America/New_York"
    }]
    departure_airport_code = "FRA"
    arrival_airport_code = "CDG"
    flights, air = get_flight_data(departure_airport_code,arrival_airport_code)
    logging.debug(air)
    flight_df = process_flight_data(flights, air)
    airports_df = get_airports_df(airports_list, ALL_AIRPORTS)


    fig = create_plot(flight_df, airports_df)
    graphJSON = fig.to_json()

    return render_template('tester.html', airports=airports_list, graphJSON=graphJSON)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    print(get_flight_data)
