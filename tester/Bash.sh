docker-compose up -d
docker-compose up --build
docker-compose logs lufth_track_data-api-1

docker exec -it lufth_track_data-mongo_l-1 /bin/bash
    mongo
    use lufth_track_data
    db.c_airports.find().pretty()
    db.c_airports.countDocuments({})
    db.c_flights_info.countDocuments({})
    db.c_flights_info.find().limit(2).pretty()

docker exec -it lufth_track_data-neo4j_l-1 /bin/bash



curl "https://api.lufthansa.com/v1/oauth/token" -X POST -d "client_id=x7qpcucksndbwugshshxnapdp" -d "client_secret=44Ws7QrHr4" -d "grant_type=client_credentials"


curl -H "Authorization: Bearer 7dgm376mhy58xg5dfsnv4eyf" -H "Accept: application/json" https://api.lufthansa.com/v1/mds-references/airports/FRA

curl -H "Authorization: Bearer 7dgm376mhy58xg5dfsnv4eyf" -H "Accept: application/json" https://api.lufthansa.com/v1/mds-references/operations/schedules/FRA/JFK/2023-11-14

curl -H "Authorization: Bearer 5272xy26yc29f3g4cycqu7w3" -H "Accept: application/json" https://api.lufthansa.com/v1/mds-references/aircraft

curl -H "Authorization: Bearer 7dgm376mhy58xg5dfsnv4eyf" -H "Accept: application/json" https://api.lufthansa.com/v1/mds-references/aircraft/100

curl -H "Authorization: Bearer xcayemas3j29y2y3xejsj6ms" -H "Accept: application/json" https://api.lufthansa.com/v1/operations/schedules/FRA/JFK/2023-11-17
curl -H "Authorization: Bearer xcayemas3j29y2y3xejsj6ms" -H "Accept: application/json" https://api.lufthansa.com/v1/operations/flightstatus/route/FRA/JFK/2023-11-17

Création d'un package avec setup et faire la config avec 
##########################################################

Neo4j:
MATCH (a:Airport {nom: 'FRA'})-[r:SINGLE_FLIGHT]->(n)
RETURN a,n