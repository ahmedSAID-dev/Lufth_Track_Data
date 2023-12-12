import requests
import configparser
import os

def get_auth_token():
    """
    get the authentication token
    :return: auth token
    """
    # read config file
    config = configparser.ConfigParser()
    if os.path.exists('config.conf'):
        config.read('config.conf')
    else:
        # Chercher dans le dossier <link>lufth_o_api</link>
        lufth_o_api_path = '../lufth_o_api/config.conf'
        if os.path.exists(lufth_o_api_path):
            config.read(lufth_o_api_path)
        else:
            print("Le fichier config.conf n'a pas été trouvé.")
    
    # set variables
    secret = config['LUFTH_OPENAPI']['LUFTH_SECRET']
    key = config['LUFTH_OPENAPI']['LUFTH_KEY']
    token_url = config['LUFTH_OPENAPI']['LUFTH_TOKEN_URL']
    data = {'client_id': key, 'client_secret': secret, 'grant_type': 'client_credentials'}

    r = requests.post(token_url, data=data)
    if r.status_code == 200:
        token_string = r.json()
        return token_string['access_token']
    else:
        return 'invalid token'


def get_header():
    """
    getting the header with authorization token
    :return: header for further requests
    """
    token = get_auth_token()
    headers = {'Accept': 'application/json', 'Authorization':'Bearer '+token}
    return headers


# Test
if __name__ == "__main__":
    tk = get_auth_token()
    print(tk)