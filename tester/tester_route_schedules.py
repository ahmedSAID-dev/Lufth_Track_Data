import sys
sys.path.append('..')
from lufth_o_api import references as ref
from lufth_o_api import operations as ope
from pprint import pprint
import json
import time
from datetime import datetime

def get_s_flights(schedules):
    """
    get flight information for flight schedule as single array (without overhead from API)
    :param schedles:
    :return array with flight codes:
    """
    
    flight_clean = []
    for value in schedules:
        if isinstance(value['Flight'], list):
            connecting_flight = []
            for data in value['Flight']:
                connecting_flight.append(data)
            flight_clean.append(connecting_flight)
        if isinstance(value['Flight'], dict):
            flight_clean.append(value['Flight'])
    return flight_clean

# Test
if __name__ == "__main__":
    
    date_aujourdhui = datetime.today().strftime('%Y-%m-%d')
    
    def generate_couples(liste):
        couples = []
        for i in range(len(liste)):
            for j in range(i + 1, len(liste)):
                couples.append((liste[i], liste[j]))
        return couples
    
    airports = ["NUE", "FRA", "MUN", "CDG", "ORY", "BCN", "LAS", "DXB", "JFK", "PEK", "DOH"]
    airports_couples = generate_couples(airports)
    s_flights =[]
    
    for origin, destination in airports_couples:
        print('importing', origin,destination)
        # Les routes
        try:
            route = json.loads(ope.get_flight_route(origin,destination,date_aujourdhui))
            with open(f"../data_json/routes/lufth_route_{origin}_{destination}_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
                json.dump(route, write_file, indent=4)
        except json.JSONDecodeError:
            # Handle cases where ope.get_flight_route doesn't return valid JSON
            print("Erreur de récupération des documents route information")
        # pprint(route)
        
        # Les schedules
        try:
            schedules = json.loads(ope.get_flight_schedules(origin,destination,date_aujourdhui))['ScheduleResource']['Schedule']
            s_flights.append(get_s_flights(schedules)) # recuperer les vols du schedules
            with open(f"../data_json/schedules/lufth_schedules_{origin}_{destination}_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
                json.dump(schedules, write_file, indent=4)

        except json.JSONDecodeError:
            # Handle cases where ope.get_flight_schedules doesn't return valid JSON
            print("Erreur de récupération des documents de flight schedules")
        # A automatiser chaque jour à 19h

    with open(f"../data_json/s_flights/lufth_flights_{datetime.now().strftime('%Y%m%d')}_1901.json", "w") as write_file:
        json.dump(s_flights, write_file, indent=4)        

 
        
    
    # print(ref.get_airport_data("DXB"))
'''
    # A Recuperation de toutes les données :
    all_airports = ref.get_all_airports()
    # all_airlines = json.loads(ref.get_all_airlines())
    with open(f"../data_json/lufth_all_airports_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
        json.dump(all_airports, write_file, indent=4)
'''