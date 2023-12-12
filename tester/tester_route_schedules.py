import sys
sys.path.append('..')
from lufth_o_api import references as ref
from lufth_o_api import operations as ope
from pprint import pprint
import json
import schedule
import time
from datetime import datetime

# Test
if __name__ == "__main__":
    tk = ref.get_aircraft_data()
    route = ope.get_flight_route("FRA","JFK","2023-12-12")
    schedules = ope.get_flight_schedules("FRA","JFK","2023-12-12")
    pprint(route)
    
    # A automatiser chaque jour à 19h
    with open(f"../data_json/lufth_schedules_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
        json.dump(schedules, write_file, indent=4)
    with open(f"../data_json/lufth_route_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
        json.dump(route, write_file, indent=4)