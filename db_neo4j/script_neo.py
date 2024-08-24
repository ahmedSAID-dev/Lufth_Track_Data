import logging
import requests
import time
import pymongo
import json
import os
from neo4j import GraphDatabase

# Création du dossier logs s'il n'existe pas
if not os.path.exists("./app/logs"):
    os.makedirs("./app/logs")
# Configuration du logging
log_file = "./app/logs/neo4jupload.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# Configuration de l'URL de Neo4j
NEO4J_URL = "http://neo4j_l:7474/browser/"
DELETE_EXISTING_DATA = True
node_counter = 0  # Initialize counter for created nodes
relation_counter = 0

# Fonction pour envoyer une requête "heartbeat"
def send_heartbeat():
    try:
        response = requests.get(f"{NEO4J_URL}")
        if response.status_code == 200:
            return True
    except Exception:
        pass
    return False

# Délai entre les requêtes "heartbeat"
HEARTBEAT_DELAY = 5  # secondes

def create_flight_relations(driver, departure_airport, arrival_airport, flight_type, flight_data):
    """
    Crée une relation entre deux aéroports dans Neo4j représentant un vol.

    Args:
        driver (neo4j.Driver): Objet Driver Neo4j pour la connexion à la base de données Neo4j.
        departure_airport (str): Code de l'aéroport de départ.
        arrival_airport (str): Code de l'aéroport d'arrivée.
        flight_type (str): Type de vol ('single flight' ou 'connecting flight').
        flight_data (dict): Données du vol contenant les informations supplémentaires.

    Returns:
        None
    """
    if flight_type == "single flight":
        relationship_type = "SINGLE_FLIGHT"
    elif flight_type == "connecting flight":
        relationship_type = "CONNECTING_FLIGHT"

    query = f"""
    MATCH (dep:Airport {{nom: $departure_airport}})
    MATCH (arr:Airport {{nom: $arrival_airport}})
    CREATE (dep)-[:{relationship_type} {{
        scheduled_departure_time_utc: $scheduled_departure_time_utc,
        actual_departure_time_utc: $actual_departure_time_utc,
        departure_time_status: $departure_time_status,
        scheduled_arrival_time_utc: $scheduled_arrival_time_utc,
        actual_arrival_time_utc: $actual_arrival_time_utc,
        arrival_time_status: $arrival_time_status,
        marketing_carrier: $marketing_carrier,
        equipment: $equipment,
        flight_status: $flight_status
    }}]->(arr)
    """
    params = {
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
        "scheduled_departure_time_utc": flight_data["Departure"]["ScheduledTimeUTC"]["DateTime"],
        "actual_departure_time_utc": flight_data["Departure"]["ActualTimeUTC"]["DateTime"],
        "departure_time_status": flight_data["Departure"]["TimeStatus"]["Definition"],
        "scheduled_arrival_time_utc": flight_data["Arrival"]["ScheduledTimeUTC"]["DateTime"],
        "actual_arrival_time_utc": flight_data["Arrival"]["ActualTimeUTC"]["DateTime"],
        "arrival_time_status": flight_data["Arrival"]["TimeStatus"]["Definition"],
        "marketing_carrier": flight_data["MarketingCarrier"]["AirlineID"] + flight_data["MarketingCarrier"]["FlightNumber"],
        "equipment": flight_data["Equipment"]["AircraftCode"],
        "flight_status": flight_data["FlightStatus"]["Definition"]
    }

    try:
        with driver.session() as session:
            session.run(query, params)
        logging.info(f"Relation créée entre {departure_airport} et {arrival_airport} pour le vol de type {flight_type}.")
    except Exception as e:
        logging.error(f"Erreur lors de la création de la relation : {e}")

def create_flight_relations_basic(driver, departure_airport, arrival_airport, flight_type, flight_data):
    """
    Crée une relation entre deux aéroports dans Neo4j représentant un vol.

    Args:
        driver (neo4j.Driver): Objet Driver Neo4j pour la connexion à la base de données Neo4j.
        departure_airport (str): Code de l'aéroport de départ.
        arrival_airport (str): Code de l'aéroport d'arrivée.
        flight_type (str): Type de vol ('single flight' ou 'connecting flight').
        flight_data (dict): Données du vol contenant les informations supplémentaires.

    Returns:
        None
    """
    if flight_type == "single flight":
        relationship_type = "SINGLE_FLIGHT"
    elif flight_type == "connecting flight":
        relationship_type = "CONNECTING_FLIGHT"
    flight_status = flight_data["FlightStatus"]["Definition"]

    query = f"""
    MATCH (dep:Airport {{nom: $departure_airport}})
    MATCH (arr:Airport {{nom: $arrival_airport}})
    CREATE (dep)-[:{relationship_type}{{nom: $arrival_airport}}]->(arr)
    """
    params = {
        "departure_airport": departure_airport,
        "arrival_airport": arrival_airport,
     }

    try:
        with driver.session() as session:
            session.run(query, params)
        logging.info(f"Relation créée entre {departure_airport} et {arrival_airport} pour le vol de type {flight_type}.")
    except Exception as e:
        logging.error(f"Erreur lors de la création de la relation : {e}")


while True:
    # Envoi d'une requête "heartbeat"
    heartbeat_success = send_heartbeat()
    # Si Neo4j répond, lancez le script principal
    if heartbeat_success:
        print("Neo4j est disponible. Lancement du script principal...")
        
        # Assurer que le scrapping est complet
        completion_signal_file = "./data_json/completion_signal_mango.txt"
        while not os.path.exists(completion_signal_file):
            time.sleep(20)  # Attendre 20 secondes avant de vérifier à nouveau
            logging.debug("Le fichier de signalisation Mango n'est pas encore présent.")
            print("Téléchargement des données toujours en cours. Attente...")
        
        # Configuration de la connexion à MongoDB
        try:
            client_mongo = pymongo.MongoClient("mongodb://mongo_l:27017")
            logging.info("Connexion à MongoDB réussie")
        except pymongo.errors.ConnectionFailure as e:
            logging.error(f"Erreur de connexion à MongoDB : {e}")
            exit()

        db_mongo = client_mongo["lufth_track_data"]
        collection_airpots = db_mongo["c_airports"]
        collection_flights_info = db_mongo["c_flights_info"]

        # Configuration de la connexion à Neo4j
        try:
            uri = "bolt://neo4j_l:7687"
            driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
            logging.info("Connexion à Neo4j réussie")
        except Exception as e:
            logging.error(f"Erreur de connexion à Neo4j : {e}")
            exit()

        # Requête pour récupérer les données de MongoDB
        logging.info("Récupération des documents MongoDB")
        try:
            documents_airports = collection_airpots.find({})
        except pymongo.errors.CursorNotFound as e:
            logging.error(f"Erreur de récupération des documents : {e}")
            exit()
        
        # Supression des données existantes
        if DELETE_EXISTING_DATA:
            logging.info("Suppression des données Neo4j existantes...")
            query = """
            MATCH (n)
            DETACH DELETE n
            """
            try:
                with driver.session() as session:
                    session.run(query)
            except Exception as e:
                logging.error(f"Erreur de suppression des données : {e}")
        
        # Création de noeuds airport Neo4j
        for document in documents_airports:
            logging.info(f"Création du noeud Neo4j pour {document['AirportCode']}")
            # Création d'un noeud avec label "Document" et propriétés
            if "CountryCode" in document:
                pays = document["CountryCode"]
            else:
                pays = "Inconnu"

            query = f"""
            CREATE (n:Airport {{
            nom: $nom,
            pays: $pays,
            Latitude: $Latitude,
            Longitude: $Longitude
            }})
            """
            params = {"nom": document["AirportCode"], "pays": pays,
                    "Latitude": document["Position"]["Coordinate"]["Latitude"], "Longitude": document["Position"]["Coordinate"]["Longitude"] }
            try:
                with driver.session() as session:
                    session.run(query, params)
                    node_counter += 1
            except Exception as e:
                logging.error(f"Erreur de création du noeud : {e}")
        logging.info(f"Nombre total de noeuds créés : {node_counter}")
        print(f"Nombre total de noeuds créés : {node_counter}")
        '''
        # Affichage des noeuds Neo4j créés
        logging.info("Affichage des noeuds Neo4j créés")
        query = """
        MATCH (n:Airport)
        RETURN n
        """
        try:
            with driver.session() as session:
                results = session.run(query)
                for result in results:
                    print(result["n"])
        except Exception as e:
            logging.error(f"Erreur d'affichage des noeuds : {e}")
        '''
        
        
        # Requête pour récupérer les données de vols depuis MongoDB
        logging.info("Récupération des documents MongoDB pour les vols")
        try:
            documents_flights_info = collection_flights_info.find({})
        except pymongo.errors.CursorNotFound as e:
            logging.error(f"Erreur de récupération des documents : {e}")
            exit()
        
        # Création des relations entre les aéroports dans Neo4j
        for flight_info in documents_flights_info:
            try:
                flight_data = json.loads(flight_info["status"])
                departure_airport = flight_data["FlightStatusResource"]["Flights"]["Flight"][0]["Departure"]["AirportCode"]
                arrival_airport = flight_data["FlightStatusResource"]["Flights"]["Flight"][0]["Arrival"]["AirportCode"]
                flight_type = flight_info["type"]
                
                logging.info(f"depart airport  : {departure_airport} arrival_airport                  : {arrival_airport}")

                create_flight_relations_basic(driver, departure_airport, arrival_airport, flight_type, flight_data)
                relation_counter += 1
            except Exception as e:
                logging.error(f"Erreur lors du traitement du vol : {e}")
        # Fermeture des connexions
        client_mongo.close()
        driver.close()
        print(f"Upload Noeuds Neo4j terminé ({node_counter} noeuds créés)")
        print(f"Création des relations entre les aéroports terminée ({relation_counter} relations créées)")
        break
    # Sinon, attendez et réessayez
    else:
        print("Neo4j n'est pas disponible. Attente...")
        time.sleep(HEARTBEAT_DELAY)

