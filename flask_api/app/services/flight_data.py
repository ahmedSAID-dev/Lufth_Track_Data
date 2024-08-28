import pymongo
import json
import re
import pandas as pd
from datetime import datetime
from ..utils.caching import cache

client = pymongo.MongoClient("mongodb://mongo_l:27017/")
db = client['lufth_track_data']

@cache.cached(timeout=3600)
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
                        print(flight_detail.get('Departure'))
                        origin = next((airport for airport in airports if airport['AirportCode'] == flight_detail['Departure']['AirportCode']), None)
                        destination = next((airport for airport in airports if airport['AirportCode'] == flight_detail['Arrival']['AirportCode']), None)
                        if origin and destination:
                            flight_type = flight['type']
                            time_status = flight_detail['Departure']['TimeStatus']['Definition'] if 'TimeStatus' in flight_detail['Departure'] else None
                            flight_number = flight_detail['MarketingCarrier']['FlightNumber']
                            departure_date = flight_detail['Departure']['ScheduledTimeLocal']['DateTime']
                            delay_minutes = 0
                            if 'Flight Delayed' in time_status:
                                scheduled_time = datetime.fromisoformat(flight_detail['Departure']['ScheduledTimeLocal']['DateTime']) if 'ScheduledTimeLocal' in flight_detail['Departure'] else None
                                actual_time = datetime.fromisoformat(flight_detail['Departure']['ActualTimeLocal']['DateTime']) if 'ActualTimeLocal' in flight_detail['Departure'] else scheduled_time
                                delay = actual_time - scheduled_time
                                delay_minutes = delay.total_seconds() / 60
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
                                'delay_minutes': delay_minutes,
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
                                    f"Delay Min: {delay_minutes}"
                                )
                            })
            except json.JSONDecodeError:
                continue
    return pd.DataFrame(flight_data)
