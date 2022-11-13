from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from wewriters.db import get_db

input = Blueprint('input', __name__)

@input.route('/add/project/', methods = ['POST', 'GET'])
def addProject():

    con = get_db()
    cur = con.cursor()

    sql = "SELECT C.cname AS cname, C.cid AS cid, count(PC.pid) AS count FROM categories C LEFT JOIN projectcategories PC ON PC.cid = C.cid  GROUP BY C.cid ORDER BY count DESC"
    cur.execute(sql)
    categories = cur.fetchall()

    available = []
    for category in categories:
        available.append(category['cid'])

    if request.method == 'POST':
        pname = request.form.get('Name')
        category = request.form.get('Category')
        description = request.form.get('Description')
        
        
        sql = "INSERT INTO projects (pname, description, uid) VALUES (%s, %s, %s) RETURNING pid"

        # TODO: error check!
        cur.execute(sql, (pname, description, current_user.uid))
        pid = cur.fetchone()['pid']

        # extract categories
        selected = []
        for each in available:
            if request.form.get(str(each)) == "on":
                selected.append((each,pid))

        # prepare for multiple inserts
        args = ','.join(cur.mogrify("(%s,%s)", i).decode('utf-8')
                for i in selected)

        sql = "INSERT INTO projectcategories (cid, pid) VALUES "
        # TODO: error check!
        cur.execute(sql + args)

        con.commit()
        
        flash('Your project {} has been added!'.format(pname), category="message")

        # need to do all checks before proceeding!
        return redirect(url_for('main.index'))   
    


    return render_template('add-project.html', title = "Add Project", categories = categories)

@input.route('/add/block/')
def addBlock():

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        pid=1

        title = request.form.get('Title')
        text = request.form.get('Text')

        sql = "INSERT INTO blocks (title, text, pid) VALUES (%s, %s,%s)"

        try: 
            cur.execute(sql, (title, text, pid,))
            con.commit()
            flash("Block {} successfully added!".format(title), category="message")
            return redirect(url_for('input.project'))
        except:
            flash("Block {} couldn't be added. It probably already exists!".format(title), category="error")


    return render_template('add-block.html')


@input.route('/add/announcement/')
def addAnnouncement():

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        pid=1

        title = request.form.get('Title')
        text = request.form.get('Text')

        sql = "INSERT INTO announcements (title, text, pid) VALUES (%s, %s, %s)"

        try: 
            cur.execute(sql, (title, text, pid,))
            con.commit()
            flash("Announcement {} successfully added!".format(title), category="message")
            return redirect(url_for('input.addProject'))
        except:
            flash("Announcement {} couldn't be added. It probably already exists!".format(title), category="error")


    return render_template('add-announcement.html')


@input.route('/add/note/')
def addNote():

    if request.method == 'POST':

        pid=1

        con = get_db()
        cur = con.cursor()

        title = request.form.get('Title')
        text = request.form.get('Text')

        sql = "INSERT INTO notes (title, text, pid, uid) VALUES (%s, %s, %s, %s)"

        try: 
            cur.execute(sql, (title, text, pid, current_user.uid,))
            con.commit()
            flash("Note {} successfully added!".format(title), category="message")
            return redirect(url_for('input.addProject'))
        except:
            flash("Note {} couldn't be added. It probably already exists!".format(title), category="error")


    return render_template('add-note.html')


@input.route('/add/tag/', methods = ['POST', 'GET'])
def addTag():

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        tag = request.form.get('Tag')

        sql = "INSERT INTO tags (name) VALUES (%s)"

        try: 
            cur.execute(sql, (tag,))
            con.commit()
            flash("Tag {} successfully added!".format(tag), category="message")
            return redirect(url_for('input.addProject'))
        except:
            flash("Tag {} couldn't be added. It probably already exists!".format(tag), category="error")


    return render_template('add-tag.html')


@input.route('/add/reply/')
def addReply():

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        nid = 2

        text = request.form.get('Text')

        sql = "INSERT INTO replies (name) VALUES (%s, %s, %s)"

        try: 
            cur.execute(sql, (text, nid, current_user.uid,))
            con.commit()
            flash("Reply {} successfully added!".format(text), category="message")
            return redirect(url_for('input.addProject'))
        except:
            flash("Reply {} couldn't be added. It probably already exists!".format(text), category="error")


    return render_template('add-reply.html')

@input.route('/add/category/', methods = ['POST', 'GET'])
def addCategory():

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        category = request.form.get('Category')

        sql = "INSERT INTO Categories (cname) VALUES (%s)"

        try: 
            cur.execute(sql, (category,))
            con.commit()
            flash("Category {} successfully added!".format(category), category="message")
            return redirect(url_for('input.addProject'))
        except:
            flash("Category {} couldn't be added. It probably already exists!".format(category), category="error")
        

    return render_template('add-category.html')