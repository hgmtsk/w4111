from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash

from wewriters.db import get_db

from .user import User

auth = Blueprint('auth', __name__)

@auth.route('/register/')
def register():
    return render_template("register.html", title = "Registration")


@auth.route('/register/', methods=['POST'])
def register_post():

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    print(email,username,password)

    # TODO: error check (rando + user exists)

    con = get_db()
    cur = con.cursor()

    sql = "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING uid"

    cur.execute(sql, (username, email,))

    uid = cur.fetchone()['uid']
    
    sql = "INSERT INTO auth (uid, hpwd) VALUES (%s, %s)"

    cur.execute(sql, (uid, generate_password_hash(password, method='sha256'),))

    con.commit()
    
    login_user(User(str(uid)))

    flash("Registration successful. Welcome, {}!".format(username), category="message")

    return redirect(url_for("main.index"))


@auth.route('/login/')
def login():
    return render_template("login.html", title = "Login")


@auth.route('/login/', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    con = get_db()
    cur = con.cursor()

    sql = "SELECT U.uid AS uid, U.username AS username, A.hpwd AS hpwd FROM Users AS U, Auth AS A WHERE U.email = %s AND U.uid = A.uid"

    cur.execute(sql,(email,))
    res = cur.fetchone()

    if check_password_hash(res['hpwd'], password):

        login_user(User(str(res['uid'])))

        flash("Registration successful. Welcome, {}!".format(res['username']), category="message")

        return redirect(url_for("main.index"))

    flash("Login unsuccessful. Wrong email or password. Try again.", category="error")

    return render_template("login.html", title = "Login")

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


