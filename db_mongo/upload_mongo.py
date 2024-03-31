import os
import json
import logging
from pymongo import MongoClient

# Configuration de la journalisation
logging.basicConfig(level=logging.DEBUG)

# Définition du chemin vers le répertoire contenant les fichiers JSON des vols
json_flights_dir = "/data_json/flights_info/"

def connect_to_mongodb(url, db_name):
    """
    Se connecte à MongoDB.

    Args:
        url (str): URL de la base de données MongoDB.
        db_name (str): Nom de la base de données à utiliser.

    Returns:
        MongoClient: Objet MongoClient connecté à la base de données.
    """
    
    try:
        client = MongoClient(url)
        db = client[db_name]
        logging.debug("Connexion à MongoDB établie avec succès.")
        return db
    except Exception as e:
        logging.error(f"Erreur lors de la connexion à MongoDB : {e}")
        raise

def load_flights_data(directory):
    """
    Charge les données des vols à partir des fichiers JSON dans un répertoire.

    Args:
        directory (str): Chemin vers le répertoire contenant les fichiers JSON des vols.

    Returns:
        list: Liste des données des vols.
    """
    flights_data = []
    for filename in os.listdir(directory):
        if filename.endswith("_flights_info.json"):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                flights_data.extend(data)
                logging.debug(f"Chargement des données du fichier {filename} des vols réussi.")
            except FileNotFoundError:
                logging.error(f"Le fichier {filename} des vols est introuvable.")
            except Exception as e:
                logging.error(f"Erreur lors du chargement du fichier {filename} des vols : {e}")
    return flights_data

if __name__ == "__main__":
    # Variables de configuration MongoDB
    mongodb_url = "mongodb://mongo_l:27017/"
    database_name = "lufth_track_data"
    
    # Connexion à MongoDB
    db = connect_to_mongodb(mongodb_url, database_name)
    c_airports = db["c_airports"]
    c_flights_info = db["c_flights_info"]

    # Charger les données des aéroports et les insérer dans MongoDB
    try:
        with open("./data_json/lufth_all_airports.json", "r") as f:
            airports_data = json.load(f)
        c_airports.insert_many(airports_data)
        logging.info("Upload réussi des données des aéroports vers MongoDB.")
    except FileNotFoundError:
        logging.error("Le fichier des aéroports est introuvable.")
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion des données des aéroports dans MongoDB : {e}")

    # Charger les données des vols et les insérer dans MongoDB
    try:
        flights_data = load_flights_data(json_flights_dir)
        c_flights_info.insert_many(flights_data)
        logging.info("Upload réussi des données des vols vers MongoDB.")
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion des données des vols dans MongoDB : {e}")

    logging.info("Upload de tous les fichiers JSON vers MongoDB terminé.")
