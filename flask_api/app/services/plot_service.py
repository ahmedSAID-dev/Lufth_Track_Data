# app/services/plot_service.py

import plotly.graph_objects as go

# Création du graphique Plotly interactif
def create_plot(flight_df, airports_df):
    """
    Crée un graphique Plotly interactif pour visualiser les vols et les aéroports.
    
    Args:
        flight_df (pd.DataFrame): Un DataFrame contenant les données des vols.
        airports_df (pd.DataFrame): Un DataFrame contenant les données des aéroports.
    
    Returns:
        go.Figure: Une figure Plotly contenant le graphique.
    """
    fig = go.Figure()

    # Créer des traces pour chaque ligne de vol
    for _, row in flight_df.iterrows():
        if row['line_type'] == 'connecting':
            fig.add_trace(go.Scattermapbox(
                lat=[row['origin_lat'], row['destination_lat']],
                lon=[row['origin_lon'], row['destination_lon']],
                mode='lines',
                line=dict(width=2, color=row['color']),
                # line=dict(width=2, color=row['color'], symbol= 'arrow'),
                hoverinfo='text',
                hovertext=row['hover_text'],
                name=f"CONNECTING {row['flight_number']} from {row['origin_code']} to {row['destination_code']}"
            ))
        else:
            fig.add_trace(go.Scattermapbox(
                lat=[row['origin_lat'], row['destination_lat']],
                lon=[row['origin_lon'], row['destination_lon']],
                mode='lines',
                line=dict(width=3, color=row['color']),
                hoverinfo='text',
                hovertext=row['hover_text'],
                name=f"SINGLE {row['flight_number']} from {row['origin_code']} to {row['destination_code']}"
            ))

    # Ajouter les points d'aéroport à la carte
    for _, airport in airports_df.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[airport['Latitude']],
            lon=[airport['Longitude']],
            mode='markers+text',
            marker=dict(size=10, color='black'),
            text=airport['AirportCode'],
            textposition='top center',
            hoverinfo='text',
            hovertext=f"Aéroport: {airport['Name']} ({airport['AirportCode']})",
            name=f"{airport['Name']}"
        ))
    # Ajouter legende satut couleur
    status_colors = {
        "Flight On Time": "blue",
        "Flight Early": "green",
        "Flight Delayed": "red"
    }
    for status, color in status_colors.items():
        fig.add_trace(go.Scattermapbox(
            lat=[None],  # Dummy value
            lon=[None],  # Dummy value
            mode='markers',
            marker=dict(size=10, color=color),
            name=status,
            showlegend=True
        ))
    fig.update_layout(
        title='Flights and Airports',
        mapbox=dict(
            style='open-street-map',
            zoom=2
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    return fig