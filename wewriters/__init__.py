import os

from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route('/hello')
    def hello():
        return 'Hey Marc!'

    @app.route('/broadway')
    def new():
        return '<b> We should go to a Broadway show </b> sssss'

    return app
