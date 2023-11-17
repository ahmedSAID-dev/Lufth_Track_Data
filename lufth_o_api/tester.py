import references as ref
import operations as ope
from pprint import pprint
import json
import schedule
import time
from datetime import datetime
# Test
if __name__ == "__main__":
    tk = ref.get_aircraft_data()
    route = ope.get_flight_route("FRA","JFK","2023-11-17")
    pprint(route)
    
    # A automatiser chaque jour à 19h
    with open(f"lufth_{datetime.now().strftime('%Y%m%d')}_1900.json", "w") as write_file:
        json.dump(route, write_file)