import json
import sys
sys.path.append('..') # à optimiser
from lufth_o_api import references as ref
import lufth_o_api as ope
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
    query_FRA_JFK = {
        'origin': 'FRA',
        'destination': 'JFK',
        'date': date_aujourdhui}
    print(get_flights(query_FRA_JFK))
    p_flight_info = publish_flight_information(get_flights(query_FRA_JFK), query_FRA_JFK)
    # publish_flight_information(get_flights(query_FRA_JFK), query_FRA_JFK)
    
    # A automatiser chaque jour à 19h
    with open(f"../data_json/lufth_p_flight_info_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
        json.dump(p_flight_info, write_file, indent=4)