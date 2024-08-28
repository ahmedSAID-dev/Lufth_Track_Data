from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from ..services.flight_data import get_flight_data, process_flight_data
from ..services.airport_data import get_airports_df
from ..services.plot_service import create_plot
from config import Config

main_blueprint = Blueprint('main', __name__, template_folder='../../templates', static_folder='../static')

@main_blueprint.route('/')
def home():
    return redirect(url_for('auth.login'))

@main_blueprint.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Route principale de l'application Flask. Affiche la page d'accueil avec le graphique des vols et des aéroports.
    
    Returns:
        str: Le rendu de la page d'accueil.
    """
    flights, airports = get_flight_data()
    flight_df = process_flight_data(flights, airports)
    airports_df = get_airports_df(Config.FILTRED_AIRPORT_LIST, Config.ALL_AIRPORTS)

    if request.method == 'POST':
        flight_type = request.form['flightType']
        if flight_type == 'single':
            filtered_df = flight_df[flight_df['line_type'] == 'single']
        elif flight_type == 'connecting':
            filtered_df = flight_df[flight_df['line_type'] == 'connecting']
        else:
            filtered_df = flight_df

        fig = create_plot(filtered_df, airports_df)
        graphJSON = fig.to_json()
        return jsonify(graphJSON=graphJSON)

    fig = create_plot(flight_df, airports_df)
    graphJSON = fig.to_json()
    return render_template('index.html', graphJSON=graphJSON)
