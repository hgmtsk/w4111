import psycopg2, psycopg2.extras

import click
from flask import current_app, g




def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(dbname=current_app.config['POSTGRES_DB'],
                                user=current_app.config['POSTGRES_USER'],
                                password=current_app.config['POSTGRES_PW'],
                                host=current_app.config['POSTGRES_URL'],
                                cursor_factory=psycopg2.extras.RealDictCursor
        )
        

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()