import database_sqlite as db

# Tester les fonctions de récupération d'informations

# Alimenter la base de données

# Mettre à jour la table des aéroports
print("Mise à jour de la table des aéroports...")
nb_airports = db.update_airports()
print(f"{nb_airports} aéroports ajoutés")

# Mettre à jour la table des avions
print("Mise à jour de la table des avions...")
nb_aircrafts = db.update_aircrafts()
print(f"{nb_aircrafts} avions ajoutés")

# Mettre à jour la table des compagnies aériennes
print("Mise à jour de la table des compagnies aériennes...")
nb_airlines = db.update_airlines()
print(f"{nb_airlines} compagnies aériennes ajoutées")
# Exemple d'avion
aircraft_code = "A380"
aircraft_info = db.get_aircraft_information(aircraft_code)
print(f"Informations sur l'avion {aircraft_code} :")
print(aircraft_info)

# Exemple d'aéroport
airport_code = "CDG"
airport_info = db.get_airport_information(airport_code)
print(f"Informations sur l'aéroport {airport_code} :")
print(airport_info)

# Exemple de compagnie aérienne
airline_id = "TU"
airline_info = db.get_airline_information(airline_id)
print(f"Informations sur la compagnie aérienne {airline_id} :")
print(airline_info)