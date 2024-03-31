from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from sqlite3 import connect
from neo4j import GraphDatabase

# Définir les clients des bases de données
client_mongo = MongoClient("mongodb://mongo:27017")
db_mongo = client_mongo["lufth_track_data"]

conn_sqlite = connect("sqlite:lufth_track_data.db")
c_sqlite = conn_sqlite.cursor()

driver_neo4j = GraphDatabase("neo4j://neo4j:7687", auth=("neo4j", "password"))

app = FastAPI()

@app.post("/import_json")
async def import_json(request: Request):
    data = await request.json()
    collection = db_mongo[data["collection"]]
    collection.insert_many(data["data"])
    return {"message": "Données JSON importées avec succès"}

@app.get("/search_airport")
async def search_airport(iata_code: str):
    # Rechercher l'aéroport dans SQLite
    c_sqlite.execute("""
        SELECT * FROM airports WHERE iata_code = ?
    """, (iata_code,))
    airport = c_sqlite.fetchone()

    if not airport:
        raise HTTPException(status_code=404, detail="Aéroport introuvable")

    # Rechercher les vols liés à l'aéroport dans Neo4j
    query = f"""
        MATCH (a:Airport {{iata_code: '{iata_code}'}})
        MATCH (a)-[:CONNECTED_TO]-(b:Airport)
        RETURN a, b
    """
    results = driver_neo4j.run(query)

    return {"airport": airport, "connected_airports": [result["b"] for result in results]}

# Ajouter d'autres API pour les autres fonctionnalités

