from flask import Flask, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user
from authlib.integrations.flask_client import OAuth as fOAuth  # new version of OAuth -compartable with FedEx

import os

f_oauth = fOAuth()

def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


def create_app():
    app = Flask(__name__, template_folder='templates', static_url_path='', static_folder='static')

    # configure persistent session cache
    # Session(app)

    app.config.from_pyfile("default_settings.py")
    app.config.from_pyfile("config.py", silent=True)

    user_table = f"{app.config['USER']}Users"

    if app.config["CLIENT_SECRET"] is not None:
        os.environ["CLIENT_SECRET"] = app.config["CLIENT_SECRET"]
    if app.config["CLIENT_ID"] is not None:
        os.environ["CLIENT_ID"] = app.config["CLIENT_ID"]
    if app.config["DEBUG"] is not None:
        os.environ["DEBUG"] = str(int(app.config["DEBUG"]))

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    f_oauth.init_app(app)

    from .models import User

    if app.config["ENV"] != "production":
        # allow oauth2 loop to run over http (used for local testing only)
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query(email=user_id, table=user_table)

    @app.before_request
    def check_route_access():
        try:
            if current_user.get_id() is None and app.config["ENV"] != "production":
                user = User.query(email=app.config['EMAIL'], table=f"{app.config['USER']}Users")
                login_user(user, remember=True)
            if current_user.is_authenticated or getattr(app.view_functions[request.endpoint], 'is_public', False):
                return
            else:
                return redirect(url_for('auth.login'))
        except Exception as e:
            app.logger.error(f"Error checking route access: {e}")
            return redirect(url_for('auth.login'))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for xero parts of app
    from .xero import xero_app as xero_blueprint
    app.register_blueprint(xero_blueprint, url_prefix='/xero')

    # blueprint for FedEx parts of app
    from .blueprints.fedex_api.routes import fedex as fedex_blueprint
    app.register_blueprint(fedex_blueprint, url_prefix='/fedex')

    return app
