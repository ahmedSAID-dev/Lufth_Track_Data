import logging
import requests
import time
import pymongo
from neo4j import GraphDatabase

# Configuration de la journalisation
# logging.basicConfig(level=logging.DEBUG)

# Configuration de l'URL de Neo4j
NEO4J_URL = "http://neo4j_l:7474/browser/"
DELETE_EXISTING_DATA = True
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

while True:
    # Envoi d'une requête "heartbeat"
    heartbeat_success = send_heartbeat()
    # Si Neo4j répond, lancez le script principal
    if heartbeat_success:
        print("Neo4j est disponible. Lancement du script principal...")
        # Configuration de la connexion à MongoDB
        try:
            client_mongo = pymongo.MongoClient("mongodb://mongo_l:27017")
            logging.info("Connexion à MongoDB réussie")
        except pymongo.errors.ConnectionFailure as e:
            logging.error(f"Erreur de connexion à MongoDB : {e}")
            exit()

        db_mongo = client_mongo["lufth_track_data"]
        collection_mongo = db_mongo["c_airports"]

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
            documents_mongo = collection_mongo.find({})
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
        
        # Création de noeuds Neo4j
        for document in documents_mongo:
            logging.info(f"Création du noeud Neo4j pour {document['AirportCode']}")
            # Création d'un noeud avec label "Document" et propriétés
            query = f"""
            CREATE (n:Airport {{
            nom: $nom,
            pays: $pays,
            Latitude: $Latitude,
            Longitude: $Longitude
            }})
            """
            params = {"nom": document["AirportCode"], "pays": document["CountryCode"],
                    "Latitude": document["Position"]["Coordinate"]["Latitude"], "Longitude": document["Position"]["Coordinate"]["Longitude"] }
            try:
                with driver.session() as session:
                    session.run(query, params)
            except Exception as e:
                logging.error(f"Erreur de création du noeud : {e}")
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
        # Fermeture des connexions
        client_mongo.close()
        driver.close()
        print("Upload Neo4j terminé")
        break
    # Sinon, attendez et réessayez
    else:
        print("Neo4j n'est pas disponible. Attente...")
        time.sleep(HEARTBEAT_DELAY)

