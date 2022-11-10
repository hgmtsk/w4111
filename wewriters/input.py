from flask import Blueprint, render_template

from wewriters.db import get_db

input = Blueprint('input', __name__)

@input.route('/add/project/')
def addProject():

    return render_template('add.html')