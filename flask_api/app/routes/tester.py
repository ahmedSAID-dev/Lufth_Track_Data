from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from ..services.airport_data import get_airports, get_airports_df
from ..services.flight_data import get_flight_data, process_flight_data
from ..services.plot_service import create_plot
from config import Config

tester_blueprint = Blueprint('tester', __name__, template_folder='../../templates', static_folder='../static')

@tester_blueprint.route('/tester', methods=['GET', 'POST'])
@login_required
def tester():
    """
    Route principale de l'application Flask. Affiche la page d'accueil avec le graphique des vols et des aéroports.
    
    Returns:
        str: Le rendu de la page d'accueil.
    """
    graphJSON = None
    TTT = True
    airports_list = get_airports()
    # airports_list = [
    # {
    #     "AirportCode": "FRA",
    #     "Position": {
    #         "Coordinate": {
    #             "Latitude": 50.0331,
    #             "Longitude": 8.5706
    #         }
    #     },
    #     "CityCode": "FRA",
    #     "CountryCode": "DE",
    #     "LocationType": "Airport",
    #     "Names": {
    #         "Name": {
    #             "@LanguageCode": "en",
    #             "$": "Frankfurt/Main International"
    #         }
    #     },
    #     "UtcOffset": "2.0",
    #     "TimeZoneId": "Europe/Berlin"
    # },
    # {
    #     "AirportCode": "CDG",
    #     "Position": {
    #         "Coordinate": {
    #             "Latitude": 49.0097,
    #             "Longitude": 2.5478
    #         }
    #     },
    #     "CityCode": "PAR",
    #     "CountryCode": "FR",
    #     "LocationType": "Airport",
    #     "Names": {
    #         "Name": {
    #             "@LanguageCode": "en",
    #             "$": "Paris - Charles De Gaulle"
    #         }
    #     },
    #     "UtcOffset": "2.0",
    #     "TimeZoneId": "Europe/Paris"
    # },
    # {
    #     "AirportCode": "JFK",
    #     "Position": {
    #         "Coordinate": {
    #             "Latitude": 40.6397,
    #             "Longitude": -73.7789
    #         }
    #     },
    #     "CityCode": "NYC",
    #     "CountryCode": "US",
    #     "LocationType": "Airport",
    #     "Names": {
    #         "Name": {
    #             "@LanguageCode": "en",
    #             "$": "New York - JFK International, NY"
    #         }
    #     },
    #     "UtcOffset": "-4.0",
    #     "TimeZoneId": "America/New_York"
    # }]
    departure_airport_code = "FRA"
    arrival_airport_code = "CDG"
    flights, air = get_flight_data(departure_airport_code,arrival_airport_code)
    flight_df = process_flight_data(flights, air)
    airports_df = get_airports_df(Config.FILTRED_AIRPORT_LIST, Config.ALL_AIRPORTS)


    fig = create_plot(flight_df, airports_df)
    graphJSON = fig.to_json()
    
    if TTT:
        departure_airport_code = "FRA"
        arrival_airport_code = "JFK"
        # departure_airport_code = request.form.get('departureAirport')
        # arrival_airport_code = request.form.get('arrivalAirport')
        flights, air = get_flight_data(departure_airport_code,arrival_airport_code)
        flight_df = process_flight_data(flights, air)
        airports_df = get_airports_df(Config.FILTRED_AIRPORT_LIST, Config.ALL_AIRPORTS)
        fig = create_plot(flight_df, airports_df)
        graphJSON = fig.to_json()
        # return jsonify({
        #     'graphJSON': graphJSON,
        #     'departureAirportCode': departure_airport_code,
        #     'arrivalAirportCode': arrival_airport_code
        # })
        return render_template('tester.html', airports=airports_list, graphJSON=graphJSON)
    else :

        return render_template('tester.html', airports=airports_list, graphJSON=graphJSON)