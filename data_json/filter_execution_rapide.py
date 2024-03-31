import json

# Chemin vers le fichier JSON d'origine
chemin_fichier = "lufth_all_airports_backup.json"

# Liste des codes d'aéroport à conserver
codes_aeroport_a_garder = ["NUE", "FRA", "MUN", "CDG", "ORY", "BCN", "LAS", "DXB", "JFK", "PEK", "DOH"]

# Fonction pour filtrer les données du fichier JSON
def filtrer_aeroports(fichier, codes_aeroport):
    with open(fichier, "r") as f:
        data = json.load(f)
    
    # Filtrer les données pour ne garder que les aéroports avec les codes spécifiés
    aeroports_filtres = [aeroport for aeroport in data if aeroport.get("AirportCode") in codes_aeroport]
    
    return aeroports_filtres

# Appeler la fonction de filtrage
aeroports_filtres = filtrer_aeroports(chemin_fichier, codes_aeroport_a_garder)

# Écrire les données filtrées dans un nouveau fichier JSON
nouveau_chemin_fichier = "lufth_all_airports.json"
with open(nouveau_chemin_fichier, "w") as f:
    json.dump(aeroports_filtres, f, indent=4)

print("Les données ont été filtrées avec succès.")
