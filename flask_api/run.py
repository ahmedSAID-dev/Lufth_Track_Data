from app import create_app
import logging

# Créer une instance de l'application Flask
app = create_app()

# Configuration du logging
log_file = "./logs/flask.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
