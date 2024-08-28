from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from ..services.airport_data import get_airports, get_airports_df
from ..services.flight_data import get_flight_data, process_flight_data
from ..services.plot_service import create_plot
from config import Config

airport_blueprint = Blueprint('airport', __name__, template_folder='../../templates', static_folder='../static')

@airport_blueprint.route('/airport', methods=['GET', 'POST'])
@login_required
def airport():
    """
    Route pour sélectionner les aéroports de départ et d'arrivée et afficher le graphique des vols correspondants.
    
    Returns:
        str: Le rendu de la page avec le formulaire de sélection des aéroports et le graphique.
    """
    airports_ls = get_airports()
    airports_df = get_airports_df(Config.FILTRED_AIRPORT_LIST, Config.ALL_AIRPORTS)
    graphJSON = None
    error_message = None

    # Utilisation de valeurs par défaut
    departure_airport_code = "FRA"
    arrival_airport_code = "CDG"

    if request.method == 'POST':
        departure_airport_code = request.form.get('departureAirport')
        arrival_airport_code = request.form.get('arrivalAirport')

        if departure_airport_code and arrival_airport_code:
            # Récupérer les données de vol et les filtrer par les aéroports sélectionnés
            flights, airports = get_flight_data(departure_airport_code, arrival_airport_code)
            flight_df = process_flight_data(flights, airports)

            if not flight_df.empty:
                fig = create_plot(flight_df, airports_df)
                graphJSON = fig.to_json()
            else:
                graphJSON = {}
        else:
            error_message = "Aéroport non trouvé. Veuillez sélectionner des aéroports valides."

        return jsonify({
            'graphJSON': graphJSON,
            'departureAirportCode': departure_airport_code,
            'arrivalAirportCode': arrival_airport_code
        })
    else:
        # Pour le rendu initial de la page
        flights, air = get_flight_data(departure_airport_code, arrival_airport_code)
        flight_df = process_flight_data(flights, air)
        fig = create_plot(flight_df, airports_df)
        graphJSON = fig.to_json()

    return render_template('airport.html', airports=airports_ls, graphJSON=graphJSON, error_message=error_message)