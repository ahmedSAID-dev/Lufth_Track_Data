from flask import Flask
from flask_caching import Cache
from flask_login import LoginManager
from .routes import main_blueprint, auth_blueprint, airport_blueprint
from .models import User

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Secret key for sessions

    # Initialize cache
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})

    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(airport_blueprint)

    return app
