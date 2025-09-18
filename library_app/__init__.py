# library_app/__init__.py
# Haupt-Paket der Anwendung. Enthält die Application Factory `create_app`.

import os
import datetime

from flask import Flask
from flask_login import LoginManager

from .models import load_user_for_login
from .routes import main, auth, books, authors, users, api 

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.urandom(24),
    )

    # Login Manager initialisieren
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Bitte melden Sie sich an, um diese Seite aufzurufen."
    login_manager.login_message_category = "info"

    # User-Loader-Funktion registrieren
    @login_manager.user_loader
    def load_user(user_id):
        return load_user_for_login(user_id)

    # Kontextprozessor für alle Templates registrieren
    @app.context_processor
    def inject_now():
        return {'now': datetime.datetime.now(datetime.timezone.utc)}
        
    # Blueprints importieren und registrieren
    app.register_blueprint(main.main_bp)
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(books.books_bp)
    app.register_blueprint(authors.authors_bp)
    app.register_blueprint(users.users_bp)
    app.register_blueprint(api.api_bp)
    
    return app