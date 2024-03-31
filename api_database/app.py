from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from database_sqlite import (
    get_aircraft_information,
    get_airport_information,
    get_airline_information,
    update_airports,
    update_aircrafts,
    update_airlines,
)

app = FastAPI()

class AircraftRequest(BaseModel):
    aircraft_code: str

class AirportRequest(BaseModel):
    airport_code: str

class AirlineRequest(BaseModel):
    airline_id: str

# Import du SQLITE
@app.get("/aircraft/{aircraft_code}")
async def get_aircraft_information(request: Request, aircraft_request: AircraftRequest):
    aircraft_info = get_aircraft_information(aircraft_request.aircraft_code)
    if aircraft_info is None:
        raise HTTPException(status_code=404, detail="Avion introuvable")
    return aircraft_info

@app.get("/airport/{airport_code}")
async def get_airport_information(request: Request, airport_request: AirportRequest):
    airport_info = get_airport_information(airport_request.airport_code)
    if airport_info is None:
        raise HTTPException(status_code=404, detail="Aéroport introuvable")
    return airport_info

@app.get("/airline/{airline_id}")
async def get_airline_information(request: Request, airline_request: AirlineRequest):
    airline_info = get_airline_information(airline_request.airline_id)
    if airline_info is None:
        raise HTTPException(status_code=404, detail="Compagnie aérienne introuvable")
    return airline_info

@app.put("/update/airports")
async def update_airports(request: Request):
    nb_airports = update_airports()
    return {"message": f"Mise à jour des aéroports terminée. Nombre d'aéroports : {nb_airports}"}

@app.put("/update/aircrafts")
async def update_aircrafts(request: Request):
    nb_aircrafts = update_aircrafts()
    return {"message": f"Mise à jour des avions terminée. Nombre d'avions : {nb_aircrafts}"}

@app.put("/update/airlines")
async def update_airlines(request: Request):
    nb_airlines = update_airlines()
    return {"message": f"Mise à jour des compagnies aériennes terminée. Nombre de compagnies aériennes : {nb_airlines}"}

# Import du MangoDB