import request as request
import json

base_url = 'https://api.lufthansa.com/v1/references/'

def get_all_airlines():
    """
    Récupère toutes les compagnies aériennes avec pagination.

    Returns:
        list: Liste de dictionnaires représentant les compagnies aériennes.
    """
    offset = 0
    airlines = []
    while True:
        url = base_url + 'airlines/?limit=100&offset=' + str(offset)
        response = request.make_request(url)
        if response == 'invalid request':
            return airlines
        data = json.loads(response)

        airline_resource = data.get("AirlineResource", {})
        airlines_data = airline_resource.get("Airlines", {})
        airline_list = airlines_data.get("Airline", [])

        if not airline_list:
            break

        airlines.extend(airline_list)
        offset += 100

    return airlines

def get_all_airports():
    """
    Récupère tous les aéroports avec pagination.

    Returns:
        list: Liste de dictionnaires représentant les aéroports.
    """
    offset = 0
    airports = []
    while True:
        url = base_url + 'airports/?lang=EN&limit=100&LHoperated=1&offset=' + str(offset)
        response = request.make_request(url)
        if response == 'invalid request':
            return airports
        data = json.loads(response)

        airport_resource = data.get("AirportResource", {})
        airports_data = airport_resource.get("Airports", {})
        airport_list = airports_data.get("Airport", [])

        if not airport_list:
            break

        airports.extend(airport_list)
        offset += 100

    return airports

def get_all_aircrafts():
    """
    Récupère tous les avions avec pagination.

    Returns:
        list: Liste de dictionnaires représentant les avions.
    """
    offset = 0
    aircrafts = []
    while True:
        url = base_url + 'aircraft/?limit=100&offset=' + str(offset)
        response = request.make_request(url)
        if response == 'invalid request':
            return aircrafts
        data = json.loads(response)

        aircraft_resource = data.get("AircraftResource", {})
        aircraft_data = aircraft_resource.get("AircraftSummaries", {})
        aircraft_list = aircraft_data.get("AircraftSummary", [])

        if not aircraft_list:
            break

        aircrafts.extend(aircraft_list)
        offset += 100

    return aircrafts

def get_airport_data(iata_airport):
    """
    Récupère les détails d'un aéroport.

    Args:
        iata_airport (str): Code IATA de l'aéroport.

    Returns:
        dict: Dictionnaire représentant les détails de l'aéroport.
    """
    url = base_url + 'airports/' + iata_airport
    return request.make_request(url)

def get_aircraft_data(aircraft_code='ALL'):
    """
    Récupère les détails d'un avion.

    Args:
        aircraft_code (str): Code de l'avion (optionnel, par défaut 'ALL' pour tous les avions).

    Returns:
        dict: Dictionnaire représentant les détails de l'avion.
    """
    if aircraft_code == 'ALL':
        url = base_url + 'aircraft/'
    else:
        url = base_url + 'aircraft/' + aircraft_code
    return request.make_request(url)

def get_airline_data(iata_airline):
    """
    Récupère les détails d'une compagnie aérienne.

    Args:
        iata_airline (str): Code IATA de la compagnie aérienne.

    Returns:
        dict: Dictionnaire représentant les détails de la compagnie aérienne.
    """
    url = base_url + 'airlines/' + iata_airline
    return request.make_request(url)

def get_countries_data(country_code):
    """
    Récupère les détails d'un pays.

    Args:
        country_code (str): Code du pays.

    Returns:
        dict: Dictionnaire représentant les détails du pays.
    """
    url = base_url + 'countries/' + country_code
    return request.make_request(url)

def get_cities_data(city_code):
    """
    Récupère les détails d'une ville.

    Args:
        city_code (str): Code de la ville.

    Returns:
        dict: Dictionnaire représentant les détails de la ville.
    """
    url = base_url + 'cities/' + city_code
    return request.make_request(url)

def get_nearest_airports(lat, long):
    """
    Récupère les aéroports les plus proches pour une latitude et une longitude données.

    Args:
        lat (float): Latitude.
        long (float): Longitude.

    Returns:
        dict: Dictionnaire représentant les détails des aéroports les plus proches.
    """
    url = base_url + 'airports/nearest/' + str(lat) + ',' + str(long)
    return request.make_request(url)
