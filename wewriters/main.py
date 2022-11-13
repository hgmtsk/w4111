from flask import Blueprint, render_template, redirect, url_for, flash, request

from wewriters.db import get_db

main = Blueprint('main', __name__)


@main.route('/')
def index():

    # demo functionality, change later
    con = get_db() # gets the connection, need figure out the connection close

    sql = "SELECT pid, U.uid, pname,username, description, P.addTime FROM Projects as P, Users as U WHERE U.uid = P.uid" # query

    
    cur = con.cursor() # get cursor for connection

    cur.execute(sql) 

    project = cur.fetchall()




    return render_template('feed.html', title = 'We, Writers', messages = project)


@main.route('/note',  strict_slashes=False)
@main.route('/note/<nid>')
def note(nid=None):
    if nid == None:
        flash("No note selected, redirected to main page.", category="error")
        return redirect(url_for("main.index"))

    pid = 0
    uid = 0

    con = get_db()
    cur = con.cursor()

    # get note info
    sql = "SELECT pid, title, text, addtime, uid FROM notes WHERE nid = %s"
    try:
        cur.execute(sql, (nid,))
        res = cur.fetchone()
        note = {'nid': nid, 'ntitle': res['title'], 'ntext': res['text'], 'naddtime': res['addtime']}
    except: 
        flash("Selected note doesn't exist. Redirected to main page.", category="error")
        return redirect(url_for("main.index"))

    # extract ids
    uid = res['uid']
    pid = res['pid']

    # get tags
    sql = "SELECT NT.tid AS tid, T.name AS tname FROM notetags AS NT, tags AS T WHERE  NT.nid = %s AND NT.tid = T.tid"
    if cur.execute(sql, (nid,)) != None:
        # TODO: signifies error
        pass
    res = cur.fetchall()
    note['tags'] = res

    # get user info
    sql = "SELECT username FROM users WHERE uid = %s"
    if cur.execute(sql, (uid,)) != None:
        # TODO: signifies error
        pass
    res = cur.fetchone()
    user = {'uid': uid, 'uname': res['username']}

    # get project info
    sql = "SELECT pname FROM projects WHERE pid = %s"
    if cur.execute(sql, (pid,)) != None:
        # TODO: signifies error
        pass
    res = cur.fetchone()
    project = {'pid': pid, 'pname': res['pname']}

    # get replies info
    sql = "SELECT R.rid AS rid, R.text AS rtext, R.addtime AS raddtime, U.uid AS ruid, U.username AS runame FROM replies AS R, users as U WHERE R.nid = %s AND R.uid = U.uid"
    if cur.execute(sql, (nid,)) != None:
        # TODO: signifies error
        pass
    res = cur.fetchall()
    replies = res

    return render_template('note.html', title = "Note #" + str(note['nid']) + ": "+str(note['ntitle']), hide = True, note = note, user = user, project = project, replies = replies)

@main.route('/project', strict_slashes=False)
@main.route('/project/<pid>')
def project(pid=None):

    if pid == None:
        flash("No project selected, redirected to all projects.", category="error")


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    #try: later!!!
    sql = "SELECT P.pid AS pid, U.uid AS uid, P.pname AS pname, U.username AS username, P.description AS pdescription, P.addTime AS paddtime FROM Projects as P, Users as U WHERE U.uid = P.uid AND P.pid=%s" # query
    cur.execute(sql, (pid,))
    
    # doesn't work!
    
    res = cur.fetchone()
    project = {'pid': pid, 'pname': res['pname'], 'uid': res['uid'], 'username': res['username'], 'pdescription':res['pdescription'], 'paddtime': res['paddtime']}

    sql = "SELECT C.cname AS cname, C.cid AS cid FROM projects P, projectcategories PC, categories C WHERE P.pid=%s AND P.pid=PC.pid AND PC.cid=C.cid" # query
    cur.execute(sql, (pid,))
    res = cur.fetchall()
    categories = res

    sql = "SELECT bid, title, addtime FROM blocks WHERE pid=%s" # query
    cur.execute(sql, (pid,))
    res = cur.fetchall()
    blocks = res

    bcount = len(blocks)                                                 

    sql = "SELECT aid, title, addtime FROM announcements WHERE pid=%s" # query
    cur.execute(sql, (pid,)) 
    res = cur.fetchall()
    announcements = res

    acount = len(announcements)

    sql = "SELECT N.nid AS nid, N.title AS title, N.addtime AS naddtime, U.username AS username, U.uid, COUNT(R.rid) AS rcount FROM notes N, replies R, users U WHERE U.uid=N.uid AND N.pid=%s GROUP BY N.nid, U.uid" # query
    cur.execute(sql, (pid,)) 
    res = cur.fetchall()
    notes = res

    ncount = len(notes)

    for note in notes:

        sql = "SELECT T.tid AS tid, T.name AS tname FROM notetags as NT, tags as T WHERE NT.nid=%s AND NT.tid = T.tid" # query
        cur.execute(sql, (note['nid'],))
        res = cur.fetchall()
        note['tags'] = res

    #except Exception as e:
    #    print(e)
    #    flash("Selected project doesn't exist. Redirected to all projects.", category="error")
    #    return redirect(url_for("main.projects"))

    return render_template('project.html', title = "Project #" + ": "+str(project['pname']), hide = True, project = project, categories = categories, blocks = blocks, bcount = bcount, announcements = announcements, acount = acount, notes = notes, ncount = ncount)

@main.route('/announcement', strict_slashes=False)    
@main.route('/announcement/<aid>')
def announcement(aid=None):

    if aid == None:
        flash("No announcement selected, redirected to main page.", category="error")
        return redirect(url_for("main.index"))


    #later will be automatic:
    aid = 5


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    sql = "SELECT aid, title, text, users.uid, username FROM announcements, users WHERE aid=%s AND announcements.uid=users.uid" # query
    if cur.execute(sql, (aid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    announcements = {'aid': aid, 'atitle': res['title'], 'atext': res['text'], 'auid': res['users.uid'], 'ausername': res['username']}

    return render_template('project.html', title = "Project #" + str(announcements['aid']) + ": "+str(announcements['atitle']), hide = True, announcements = announcements)
    
@main.route('/block', strict_slashes=False)
@main.route('/block/<bid>')
def block(bid=None):

    if bid == None:
        flash("No block selected, redirected to main page.", category="error")
        return redirect(url_for("main.index"))


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    sql = "SELECT B.bid AS bid, B.title AS btitle, B.text AS btext, U.uid AS uid, U.username AS username, P.pid AS pid, P.pname AS pname FROM blocks AS B, users AS U, people AS P WHERE U.uid=P.uid AND P.pid=B.pid AND B.bid=%s" # query
    cur.execute(sql, (bid,))
    res = cur.fetchone()
    block = res

    return render_template('block.html', title = "Block #" + str(block['bid']) + ": "+str(block['btitle']), hide = True, block = block)

@main.route('/user', strict_slashes=False)
@main.route('/user/<uid>')
def user(uid=None):

    if uid == None:
        flash("No user selected, redirected to all users.", category="error")
        return redirect(url_for("users.index"))


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    sql = "P.pid, pname, description FROM projects AS P, users AS U WHERE P.uid=U.uid AND U.uid=%s" # query
    if cur.execute(sql, (uid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    created = {'bid': bid, 'btitle': res['B.title'], 'auid': res['U.uid'], 'busername': res['B.username'], 'bpid': res['P.pid'], 'bpname': ['P.pname']}

    return render_template('project.html', title = "Project #" + str(blocks['bid']) + ": "+str(blocks['btitle']), hide = True, blocks = blocks)


@main.route('/users/')
def users():

    con = get_db()
    cur = con.cursor()

    perpage = 10
    offset = 0

    p = request.args.get("p")

    if p != None:
        offset = p 

    sql = "SELECT count(*) FROM Users"
    cur.execute(sql)

    res = cur.fetchone()

    ucount = res['count']
    ucount10 = int((ucount-1)/10) + 1

    pages = []

    for i in range(ucount10):
        pages.append(i*10)

    sql = "SELECT * FROM Users ORDER BY regtime DESC LIMIT 10 OFFSET %s"
    cur.execute(sql, (p,))
    res = cur.fetchall()



    return render_template('users.html', title = 'Users', pages = pages, users = res)

@main.route('/projects/')
def projects():

    con = get_db()
    cur = con.cursor()

    perpage = 10
    offset = 0

    # this doesnt work please fix (likely need left join). aim: get all projects (pid, pname, paddtime), corresponding user (uid, username), and count for blocks, announcements, and notes for each project (limit by perpage and offset by offset)
    sql = "SELECT P.pid AS pid, P.pname AS pname, P.addtime AS paddtime, U.uid, U.usernanme AS uname, count(N.nid) AS ncount, count(B.bid) as bcount, count(A.ais) as acount FROM projects P, users U, blocks B, announcements A, notes N WHERE P.uid = U.uid, P.pid = B.pid, P.pid = A.aid, P.pid = B.pid GROUP BY P.pid"

    pages = [0,10,20,30]

    return render_template('projects.html', pages = pages)