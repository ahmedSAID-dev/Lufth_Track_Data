import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MONGO_URI = 'mongodb://mongo_l:27017/lufth_track_data'
    CACHE_TYPE = 'simple'
    ALL_AIRPORTS = False
    FILTRED_AIRPORT_LIST = ["FRA", "JFK", "MUC", "CDG", "DXB", "LAS", "DOH", "LAX"]
