import os
import json
import logging
import time
from pymongo import MongoClient

# Définition des chemins
json_airports_file = "./data_json/lufth_all_airports.json"
json_flights_dir = "./data_json/flights_info/"
completion_signal_file = "./data_json/completion_signal.txt"
DELETE_EXISTING_DATA = True

# Création du dossier logs s'il n'existe pas
if not os.path.exists("./app/logs"):
    os.makedirs("./app/logs")
# Configuration du logging
log_file = "./app/logs/mongoupload.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
def connect_to_mongodb(url, db_name):
    """
    Se connecte à MongoDB et retourne l'objet MongoClient.

    Args:
        url (str): URL de la base de données MongoDB.
        db_name (str): Nom de la base de données à utiliser.

    Returns:
        MongoClient: Objet MongoClient connecté à la base de données.
    """
    
    try:
        client = MongoClient(url)
        db = client[db_name]
        logging.info("Connexion à MongoDB établie avec succès.")
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
        if filename.endswith("_flight_info.json"):
            filepath = os.path.join(directory, filename)
            # print ("Upload des fichiers ", filepath)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                flights_data.extend(data)
                logging.info(f"Chargement des données du fichier {filename} des vols réussi.")
            except FileNotFoundError:
                logging.error(f"Le fichier {filename} des vols est introuvable.")
            except Exception as e:
                logging.error(f"Erreur lors du chargement du fichier {filename} des vols : {e}")
        
    print ("Upload des fichiers flight json vers mongo terminé ")
    return flights_data

def clean_collection(db, collection_name):
    """
    Nettoie la collection en supprimant tous les documents et affiche le nombre de documents supprimés.

    Args:
        db (MongoClient): Objet MongoClient connecté à la base de données.
        collection_name (str): Nom de la collection à nettoyer.
    """
    
    logging.info(f"Nettoyage de la collection {collection_name}...")
    print(f"Nettoyage de la collection {collection_name}...")
    n_documents = db[collection_name].count_documents({})
    try:
        db[collection_name].drop()
        logging.info(f"{n_documents} documents supprimés de la collection {collection_name}.")
        print(f"{n_documents} documents supprimés de la collection {collection_name}.")
    except Exception as e:
        logging.error(f"Erreur lors du nettoyage de la collection {collection_name} : {e}")

def insert_airports_data(db, filepath):
    """
    Insère les données des aéroports depuis un fichier JSON dans la collection `c_airports` et affiche le nombre de documents insérés.

    Args:
        db (MongoClient): Objet MongoClient connecté à la base de données.
        filepath (str): Chemin vers le fichier JSON des aéroports.
    """
    
    try:
        with open(filepath, "r") as f:
            airports_data = json.load(f)
        n_documents = len(airports_data)
        db["c_airports"].insert_many(airports_data)
        logging.info(f"{n_documents} documents insérés dans la collection c_airports.")
    except FileNotFoundError:
        logging.error("Le fichier des aéroports est introuvable.")
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion des données des aéroports dans MongoDB : {e}")

def insert_flights_data(db, directory):
    """
    Insère les données des vols depuis des fichiers JSON dans la collection `c_flights_info` et affiche le nombre de documents insérés.

    Args:
        db (MongoClient): Objet MongoClient connecté à la base de données.
        directory (str): Chemin vers le répertoire contenant les fichiers JSON des vols.
    """
    
    flights_data = load_flights_data(directory)
    n_documents = len(flights_data)
    try:
        db["c_flights_info"].insert_many(flights_data)
        logging.info(f"{n_documents} documents insérés dans la collection c_flights_info.")
        print(f"{n_documents} documents insérés dans la collection c_flights_info.")
    except Exception as e:
        logging.error(f"Erreur lors de l'insertion des données des vols dans MongoDB : {e}")

if __name__ == "__main__":
    # Variables de configuration MongoDB
    mongodb_url = "mongodb://mongo_l:27017/"
    database_name = "lufth_track_data"
    
    # Boucle de heartbeat pour attendre le fichier de signalisation
    logging.info("En attente du fichier de signalisation pour démarrer le script...")
    while not os.path.exists(completion_signal_file):
        time.sleep(20)  # Attendre 10 secondes avant de vérifier à nouveau
        logging.debug("Le fichier de signalisation n'est pas encore présent.")

    logging.info("Fichier de signalisation détecté. Démarrage du script...")
    
    # Connexion à MongoDB
    db = connect_to_mongodb(mongodb_url, database_name)
    
    # Nettoyage des collections
    if DELETE_EXISTING_DATA:
        clean_collection(db, "c_airports")
        clean_collection(db, "c_flights_info")

    # Insertion des données
    insert_airports_data(db, json_airports_file)
    insert_flights_data(db, json_flights_dir)
    # Création du fichier de signalisation mango
    with open("/data_json/completion_signal_mango.txt", "w") as signal_file:
        signal_file.write("Mango_upload processing completed.")
    logging.info("Upload de tous les fichiers JSON vers MongoDB terminé.")
    