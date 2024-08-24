import requests
import configparser
import os

def get_auth_token():
    """
    Récupère le jeton d'authentification à partir du fichier de configuration et le retourne.

    Returns:
        str: Jeton d'authentification.
    """
    # Lecture du fichier de configuration
    config = configparser.ConfigParser()
    if os.path.exists('config.conf'):
        config.read('config.conf')
        print(os.path('config.conf'))
    else:
        # Recherche dans le dossier lufth_o_api si le fichier n'est pas trouvé dans le dossier actuel
        lufth_o_api_path = './app/config.conf'
        if os.path.exists(lufth_o_api_path):
            config.read(lufth_o_api_path)
        else:
            print("Le fichier config.conf n'a pas été trouvé.")

    # Extraction des informations d'authentification du fichier de configuration
    secret = config['LUFTH_OPENAPI']['LUFTH_SECRET']
    key = config['LUFTH_OPENAPI']['LUFTH_KEY']
    token_url = config['LUFTH_OPENAPI']['LUFTH_TOKEN_URL']
    data = {'client_id': key, 'client_secret': secret, 'grant_type': 'client_credentials'}

    # Requête POST pour obtenir le jeton d'authentification
    r = requests.post(token_url, data=data)
    if r.status_code == 200:
        token_string = r.json()
        return token_string['access_token']
    else:
        return 'invalid token'


def get_header():
    """
    Récupère l'en-tête avec le jeton d'autorisation pour les requêtes ultérieures.

    Returns:
        dict: En-tête pour les requêtes HTTP.
    """
    # Obtenir le jeton d'authentification
    token = get_auth_token()

    # Création de l'en-tête avec le jeton d'authentification
    headers = {'Accept': 'application/json', 'Authorization':'Bearer '+token}
    return headers


# Test
if __name__ == "__main__":
    tk = get_auth_token()
    print(tk)
