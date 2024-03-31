import json
import sys
sys.path.append('..') # à optimiser
from lufth_o_api import references as ref
from lufth_o_api import operations as ope
from datetime import datetime


def get_flights(flight_query):
    """
    get flight codes for flight schedule as single array (without overhead from API)
    :param flight_query:
    :return array with flight codes:
    """
    flights = json.loads(ope.get_flight_schedules(flight_query['origin'],
                                                 flight_query['destination'],
                                                 flight_query['date']))
    flight_codes = []
    for value in flights['ScheduleResource']['Schedule']:
        if isinstance(value['Flight'], list):
            connecting_flight = []
            for data in value['Flight']:
                connecting_flight.append(
                    data['MarketingCarrier']['AirlineID'] +
                    str(data['MarketingCarrier']['FlightNumber']))
            flight_codes.append(connecting_flight)
        if isinstance(value['Flight'], dict):
            flight_codes.append(
                value['Flight']['MarketingCarrier']['AirlineID'] +
                str(value['Flight']['MarketingCarrier']['FlightNumber']))
    return flight_codes


def publish_flight_information(flight_codes, flight_query):
    """
    publish the flight status information
    :param flight_codes:
    :param flight_query:
    """
    flight_info = []

    for flight_code in flight_codes:
        if isinstance(flight_code, list):
            flight_type = 'connecting flight'
            for single_flight in flight_code:
                flight_status = ope.get_flight_status(single_flight, flight_query['date'])
                flight_info.append({'type': flight_type, 'status': flight_status})
        elif isinstance(flight_code, str):
            flight_type = 'single flight'
            flight_status = ope.get_flight_status(flight_code, flight_query['date'])
            flight_info.append({'type': flight_type, 'status': flight_status})
    return flight_info

if __name__ == "__main__":
    date_aujourdhui = datetime.today().strftime('%Y-%m-%d')
    
    airports_couples = [("FRA", "JFK"), ("FRA", "MUC"), ("CDG", "FRA"), ("MUC", "JFK"), ("CDG", "MUC")]
    query_FRA_JFK = {
        'origin': 'FRA',
        'destination': 'JFK',
        'date': date_aujourdhui}

    for origin, destination in airports_couples:
        query = {
            'origin': origin,
            'destination': destination,
            'date': date_aujourdhui
        }

        # Récupération et publication des informations de vol
        flight_codes = get_flights(query)
        flight_info = publish_flight_information(flight_codes, query)
        # publish_flight_information(get_flights(query), query_FRA_JFK)
        
        # A automatiser chaque jour à 19h
        # Enregistrement des données dans des fichiers JSON
        with open(f"../data_json/lufth_p_flight_info_{origin}_{destination}_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
            json.dump(flight_info, write_file, indent=4)

        with open(f"../data_json/lufth_get_flights_{origin}_{destination}_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
            json.dump(flight_codes, write_file, indent=4)
    
    
    
