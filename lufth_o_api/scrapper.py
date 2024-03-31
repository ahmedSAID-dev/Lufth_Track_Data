import json
from datetime import datetime
import operations as ope

def get_flights(flight_query):
    """
    Récupère les codes de vol pour la requête de vol.
    :param flight_query: Dictionnaire contenant les détails de la requête de vol.
    :return: Liste de codes de vol.
    """
    flights = json.loads(ope.get_flight_schedules(flight_query['origin'],
                                                  flight_query['destination'],
                                                  flight_query['date']))
    flight_codes = []
    for schedule in flights['ScheduleResource']['Schedule']:
        if isinstance(schedule['Flight'], list):
            connecting_flights = []
            for flight in schedule['Flight']:
                connecting_flights.append(
                    flight['MarketingCarrier']['AirlineID'] +
                    str(flight['MarketingCarrier']['FlightNumber']))
            flight_codes.append(connecting_flights)
        elif isinstance(schedule['Flight'], dict):
            flight_codes.append(
                schedule['Flight']['MarketingCarrier']['AirlineID'] +
                str(schedule['Flight']['MarketingCarrier']['FlightNumber']))
    return flight_codes

def publish_flight_information(flight_codes, flight_query):
    """
    Publie les informations sur le statut des vols.
    :param flight_codes: Liste de codes de vol.
    :param flight_query: Dictionnaire contenant les détails de la requête de vol.
    :return: Liste d'informations sur les vols.
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
    today_date = datetime.today().strftime('%Y-%m-%d')
    
    airports_pairs = [("FRA", "JFK"), ("FRA", "MUC"), ("CDG", "FRA"), ("MUC", "JFK"), ("CDG", "MUC")]
    
    for origin, destination in airports_pairs:
        query = {
            'origin': origin,
            'destination': destination,
            'date': today_date
        }

        # Récupération et publication des informations de vol
        flight_codes = get_flights(query)
        flight_info = publish_flight_information(flight_codes, query)
        
        # Enregistrement des données dans des fichiers JSON
        filename_prefix = f"lufth_{origin}_{destination}_{datetime.now().strftime('%Y%m%d')}_1900"
        with open(f"../data_json/flights_info/{filename_prefix}_flight_info.json", "w") as write_file:
            json.dump(flight_info, write_file, indent=4)

        with open(f"../data_json/flights_codes/{filename_prefix}_flight_codes.json", "w") as write_file:
            json.dump(flight_codes, write_file, indent=4)
