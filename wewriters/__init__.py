import os

from flask import Flask


from dotenv import dotenv_values


def create_app():
    app = Flask(__name__)

    envconfig = dotenv_values(".env")

    app.config['POSTGRES_USER'] = envconfig['POSTGRES_USER']
    app.config['POSTGRES_PW'] = envconfig['POSTGRES_PW']
    app.config['POSTGRES_URL'] = envconfig['POSTGRES_URL']
    app.config['POSTGRES_DB'] = envconfig['POSTGRES_DB']

    app.config['SECRET_KEY'] = envconfig['SECRET_KEY']


    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

  

    return app
