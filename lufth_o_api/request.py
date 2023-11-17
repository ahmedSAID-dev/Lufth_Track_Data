import requests
# import lufth_o_api.authentication as auth
import authentication as auth
import logging


logging.basicConfig(
    level=logging.INFO,
    filename='luth_o_api.log',
    filemode='a',
    format='%(asctime)s -%(levelname)s- %(message)s')


def make_request(url):
    """
    faire un request au URL
    :param url:
    :return json object:
    """
    header = auth.get_header()
    r = requests.get(url, headers=header)
    if r.status_code == 200:
        logging.info('request to URL ' + url + ' status: ' + str(r.status_code) + ' OK')
        return r.text
    else:
        logging.info('request to URL ' + url + ' status: ' + str(r.status_code) + ' message: '+r.text)
        return 'invalid request'