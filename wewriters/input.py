from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from wewriters.db import get_db


input = Blueprint('input', __name__)



@input.route('/add/project/', methods = ['POST', 'GET'])
@login_required
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

        try:
            cur.execute(sql, (pname, description, current_user.uid))
            pid = cur.fetchone()['pid']

            # extract categories
            selected = []
            for each in available:
                if request.form.get(str(each)) == "on":
                    selected.append((each,pid))

            if len(selected)!=0:
                # prepare for multiple inserts
                args = ','.join(cur.mogrify("(%s,%s)", i).decode('utf-8')
                        for i in selected)
                sql = "INSERT INTO projectcategories (cid, pid) VALUES "
                cur.execute(sql + args)

            con.commit()
        except:
            flash("There was a problem when adding your project. Please try agian.", category="error")
            return redirect(url_for("main.project", pid=pid))      
        
        
        flash('Your project {} has been added!'.format(pname), category="message")

        # need to do all checks before proceeding!
        return redirect(url_for('main.project', pid = pid))   
    


    return render_template('add-project.html', title = "Add Project", categories = categories)

@input.route('/add/block/', methods = ['POST', 'GET'])
@login_required
def addBlock():

    pid = request.args.get("pid")

    if pid == None and request.method == 'GET':
        flash("Cannot add a block to an unknown project. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))

    con = get_db()
    cur = con.cursor()

    if request.method == 'POST':

        title = request.form.get('Title')
        text = request.form.get('Text')
        pid = request.form.get('pid')

        sql = "INSERT INTO blocks (title, text, pid) VALUES (%s, %s,%s) RETURNING bid"

        try: 
            cur.execute(sql, (title, text, pid,))
            bid = cur.fetchone()['bid']
            con.commit()
            flash("Block '{}' successfully added!".format(title), category="message")
            return redirect(url_for('main.block', bid=bid))
        except:
            flash("Block couldn't be added.", category="error")


    return render_template('add-block.html', pid=pid, title="New block for project #{}".format(pid))


@input.route('/add/announcement/', methods = ['POST', 'GET'])
@login_required
def addAnnouncement():

    uid = current_user.id
    pid = request.args.get("pid")   

    if pid == None and request.method == 'GET':
        flash("Cannot add an announcmenet to an unknown project. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))

    
    con = get_db()
    cur = con.cursor()
    

    if request.method == 'POST':

        title = request.form.get('Title')
        text = request.form.get('Text')
        pid = request.form.get('pid')

        sql = "SELECT uid FROM Projects WHERE uid = %s AND pid = %s"
        cur.execute(sql, (uid, pid))
        if cur.fetchone() == None:
            flash("You can only add announcements to your projects. Redirected to all projects.", category="error")
            return redirect(url_for("main.projects"))

        sql = "INSERT INTO announcements (title, text, pid) VALUES (%s, %s, %s) RETURNING aid"

        try: 
            cur.execute(sql, (title, text, pid,))
            aid = cur.fetchone()['aid']
            con.commit()
            flash("Announcement '{}' successfully added!".format(title), category="message")
            return redirect(url_for('main.announcement', aid=aid))
        except:
           flash("Announcement couldn't be added.", category="error")


    return render_template('add-announcement.html', pid=pid, title = "New announcement for project #{}".format(pid))


@input.route('/add/note/', methods = ['POST', 'GET'])
@login_required
def addNote(pid = None):

    if pid == None:
        pid = request.args.get("pid")   

    if pid == None and request.method == 'GET':
        flash("Cannot add a note to an unknown project. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))

    con = get_db()
    cur = con.cursor()

    sql = "SELECT T.name AS tname, T.tid AS tid, count(NT.nid) AS count FROM tags T LEFT JOIN notetags NT ON NT.tid = T.tid  GROUP BY T.tid ORDER BY count DESC"
    cur.execute(sql)
    tags = cur.fetchall()

    available = []
    for tag in tags:
        available.append(tag['tid'])


    if request.method == 'POST':      

        title = request.form.get('Title')
        text = request.form.get('Text')
        pid = request.form.get('pid')
        

        sql = "INSERT INTO notes (title, text, pid, uid) VALUES (%s, %s, %s, %s) RETURNING nid"

        try: 
            cur.execute(sql, (title, text, pid, current_user.uid,))
            nid = cur.fetchone()['nid']

            selected = []
            for each in available:
                if request.form.get(str(each)) == "on":
                    selected.append((each,nid))

                # prepare for multiple inserts
            args = ','.join(cur.mogrify("(%s,%s)", i).decode('utf-8')
                    for i in selected)

            sql = "INSERT INTO notetags (tid, nid) VALUES "

            cur.execute(sql + args)   

            con.commit()
            flash("Note #{} successfully added!".format(nid), category="message")
            return redirect(url_for('main.note', nid = nid))
        except:
            flash("Note couldn't be added.", category="error")
            return redirect(url_for("main.projects"))

    return render_template('add-note.html', pid = pid, tags = tags, title = "Add note to project #{}".format(pid))


@input.route('/add/tag/', methods = ['POST', 'GET'])
@login_required
def addTag():

    pid = request.args.get("pid") 

    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        tag = request.form.get('Tag')
        pid = request.form.get("pid")

        sql = "INSERT INTO tags (name) VALUES (%s)"

        try: 
            cur.execute(sql, (tag,))
            con.commit()
            flash("Tag {} successfully added!".format(tag), category="message")
            return redirect(url_for('input.addNote', pid=pid))
        except:
            flash("Tag {} couldn't be added. It probably already exists!".format(tag), category="error")


    return render_template('add-tag.html', title="Add tag", pid = pid)





@input.route('/add/category/', methods = ['POST', 'GET'])
@login_required
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
        

    return render_template('add-category.html', title = "Add category")

@input.route('/add/reply/', methods = ['POST', 'GET'])
@login_required
def addReply():

    nid = request.args.get("nid")   

    if nid == None and request.method == 'GET':
        flash("Cannot add a reply to an unnown project. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))


    if request.method == 'POST':

        con = get_db()
        cur = con.cursor()

        text = request.form.get('Text')
        nid = request.form.get('nid')

        sql = "INSERT INTO replies (text, nid, uid) VALUES (%s, %s, %s)"

        try: 
            cur.execute(sql, (text, nid, current_user.uid,))
            con.commit()
            flash("Reply successfully added!", category="message")
            return redirect(url_for('main.note', nid=nid))
        except:
            flash("Reply {} couldn't be added".format(text), category="error")
    

    return render_template('add-reply.html', title = "New reply to note #{}".format(nid), nid=nid)