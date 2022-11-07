from flask import Blueprint, render_template

from wewriters.db import get_db

import psycopg2.extras



main = Blueprint('main', __name__)

@main.route('/')
def index():

    # demo functionality, change later
    con = get_db() # gets the connection, need figure out the connection close

    sql = "SELECT pid, U.uid, pname,username, description, P.addTime FROM Projects as P, Users as U WHERE U.uid = P.uid" # query

    
    cur = con.cursor() # get cursor for connection

    cur.execute(sql) 

    project = cur.fetchall()

    print(project[0]['addtime'])





    return render_template('feed.html', title = 'Main Page', messages = project)