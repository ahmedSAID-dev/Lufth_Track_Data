import request as request

base_url = 'https://api.lufthansa.com/v1/operations/'

def get_flight_schedules(origin, destination, from_date_time):
    """
    Récupère les horaires de vol pour un itinéraire spécifique et une date de départ.

    Args:
        origin (str): Code IATA de l'aéroport de départ.
        destination (str): Code IATA de l'aéroport de destination.
        from_date_time (str): Date et heure de départ au format 'YYYY-MM-DDTHH:MM:SS'.

    Returns:
        dict: Dictionnaire représentant les horaires de vol.
    """
    url = base_url + 'schedules/' + origin + '/' + destination + '/' + from_date_time
    return request.make_request(url)

def get_flight_status(flight_number, date):
    """
    Récupère le statut d'un vol pour un numéro de vol et une date donnée.

    Args:
        flight_number (str): Numéro de vol.
        date (str): Date du vol au format 'YYYY-MM-DD'.

    Returns:
        dict: Dictionnaire représentant le statut du vol.
    """
    url = base_url + 'flightstatus/' + flight_number + '/' + date
    return request.make_request(url)

def get_flight_route(origin, destination, date):
    """
    Récupère le statut des vols entre deux aéroports pour une date donnée.

    Args:
        origin (str): Code IATA de l'aéroport de départ.
        destination (str): Code IATA de l'aéroport de destination.
        date (str): Date du vol au format 'YYYY-MM-DD'.

    Returns:
        dict: Dictionnaire représentant le statut des vols entre deux aéroports.
    """
    url = base_url + 'flightstatus/route/' + origin + '/' + destination + '/' + date
    return request.make_request(url)

def get_arrivals(airport_code, from_date_time):
    """
    Récupère le statut de tous les vols arrivant à un aéroport spécifique dans une plage horaire donnée.

    Args:
        airport_code (str): Code IATA de l'aéroport.
        from_date_time (str): Date et heure de début au format 'YYYY-MM-DDTHH:MM:SS'.

    Returns:
        dict: Dictionnaire représentant le statut de tous les vols arrivant à l'aéroport.
    """
    url = base_url + 'arrivals/' + airport_code + '/' + from_date_time
    return request.make_request(url)

def get_departures(airport_code, from_date_time):
    """
    Récupère le statut de tous les vols partant d'un aéroport spécifique dans une plage horaire donnée.

    Args:
        airport_code (str): Code IATA de l'aéroport.
        from_date_time (str): Date et heure de début au format 'YYYY-MM-DDTHH:MM:SS'.

    Returns:
        dict: Dictionnaire représentant le statut de tous les vols partant de l'aéroport.
    """
    url = base_url + 'departures/' + airport_code + '/' + from_date_time
    return request.make_request(url)
