# app/routes/statistics.py

from flask import Blueprint, render_template
from flask_login import login_required
from ..services.airport_data import get_airports_df
from ..services.flight_data import get_flight_data, process_flight_data
from config import Config
import pandas as pd

# Créez un nouveau blueprint pour les statistiques
statistics_blueprint = Blueprint('statistics', __name__, template_folder='../../templates', static_folder='../static')

@statistics_blueprint.route('/statistics', methods=['GET'])
@login_required
def statistics():
    """
    Route pour afficher les statistiques des vols par aéroport de départ.
    
    Returns:
        str: Le rendu de la page des statistiques.
    """
    airports_df = get_airports_df(Config.FILTRED_AIRPORT_LIST, Config.ALL_AIRPORTS)
    statistics_data = []

    # Exemple de logique pour calculer les statistiques
    for airport_code in airports_df['AirportCode']:
        flights, airports = get_flight_data(departure_airport=airport_code, arrival_airport=None)
        flight_df = process_flight_data(flights, airports)

        # Calculer les statistiques
        total_flights = len(flight_df)
        # delayed_flights = flight_df[flight_df['time_status'] == 'Flight Delayed']
        # delayed_percentage = (len(delayed_flights) / total_flights) * 100 if total_flights > 0 else 0
        preferred_destination = flight_df['destination_code'].mode().iloc[0] if not flight_df.empty else 'N/A'
        avg_passengers = flight_df['passenger_count'].mean() if 'passenger_count' in flight_df.columns else 'N/A'
        avg_delay = flight_df[flight_df['time_status'] == 'Flight Delayed']['delay_minutes'].mean() if 'delay_minutes' in flight_df.columns else float('nan')

        # Vérifier si avg_delay est un NaN
        if not pd.isna(avg_delay):
            # Arrondir et convertir en int
            avg_delay = round(avg_delay,1)  # arrondir peut être fait directement sans conversion en int
        else:
            avg_delay = 'N/A'
        total_passengers = flight_df['passenger_count'].sum() if 'passenger_count' in flight_df.columns else 'N/A'

        statistics_data.append({
            'airport_code': airport_code,
            'total_flights': total_flights,
            # 'delayed_percentage': delayed_percentage,
            'preferred_destination': preferred_destination,
            'avg_passengers': avg_passengers,
            'avg_delay': avg_delay,
            'total_passengers': total_passengers
        })

    # Rendre le template avec les données de statistiques
    return render_template('statistics.html', statistics_data=statistics_data)
