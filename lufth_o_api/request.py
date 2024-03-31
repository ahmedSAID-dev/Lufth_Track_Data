import requests
import authentication as auth
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    filename='luth_o_api.log',
    filemode='a',
    format='%(asctime)s -%(levelname)s- %(message)s'
)


def make_request(url):
    """
    Effectue une requête à l'URL spécifiée.

    Args:
        url (str): L'URL de la requête.

    Returns:
        str: La réponse de la requête au format texte si le statut de la réponse est 200, sinon 'invalid request'.
    """
    # Obtention de l'en-tête d'authentification
    header = auth.get_header()

    # Effectuer la requête HTTP GET avec l'en-tête d'authentification
    r = requests.get(url, headers=header)

    # Vérification du statut de la réponse
    if r.status_code == 200:
        logging.info('Request to URL ' + url + ' status: ' + str(r.status_code) + ' OK')
        return r.text
    else:
        # Enregistrement d'une entrée de journal en cas d'erreur
        logging.info('Request to URL ' + url + ' status: ' + str(r.status_code) + ' message: ' + r.text)
        return 'invalid request'
