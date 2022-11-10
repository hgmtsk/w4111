import os

from flask import Flask
from flask_login import LoginManager

from dotenv import dotenv_values


def create_app():
    app = Flask(__name__)

    envconfig = dotenv_values(".env")

    app.config['POSTGRES_USER'] = envconfig['POSTGRES_USER']
    app.config['POSTGRES_PW'] = envconfig['POSTGRES_PW']
    app.config['POSTGRES_URL'] = envconfig['POSTGRES_URL']
    app.config['POSTGRES_DB'] = envconfig['POSTGRES_DB']

    app.config['SECRET_KEY'] = envconfig['SECRET_KEY']


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .user import User
    @login_manager.user_loader
    def load_user(uid):
        return (User(uid))


    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .input import input as input_blueprint
    app.register_blueprint(input_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

  

    return app
