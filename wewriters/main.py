from flask import Blueprint, render_template, redirect, url_for, flash, request

from flask_login import current_user

from wewriters.db import get_db

main = Blueprint('main', __name__)


@main.route('/')
def index():

    con = get_db()
    cur = con.cursor()

    alimit = 10
    plimit = 10

    announcements = None
    projects = None

    p = request.args.get("p")
    a = request.args.get("a")

    if p != None:
        plimit = int(p) + 10
    if a != None:
        alimit = int(a) + 10


    if current_user.is_authenticated:

        sql = "SELECT A1.aid AS aid, A1.title AS title, A1.addtime AS aaddtime, U2.uid AS uid, P1.pid AS pid, P1.pname AS pname, U2.username AS username FROM announcements AS A1, projectfollows AS PF, users AS U1, projects AS P1, users AS U2 WHERE A1.pid=PF.pid AND PF.uid=U1.uid AND U1.uid=%s AND P1.pid=PF.pid AND U2.uid=P1.uid ORDER BY aaddtime DESC LIMIT %s"
        cur.execute(sql, (current_user.id,alimit))
        res = cur.fetchall()
        announcements = res

        sql = "SELECT P1.pid AS pid, P1.pname AS pname, P1.addtime AS paddtime, P1.uid AS uid, U2.username AS username, COUNT(DISTINCT B.bid) AS blocks_count, COUNT(DISTINCT A1.aid) AS announcements_count, COUNT(DISTINCT N.nid) AS notes_count, COUNT(DISTINCT PF2.uid) AS follower_count FROM users AS U1 JOIN projectfollows AS PF1 ON PF1.uid=U1.uid JOIN projects AS P1 ON U1.uid=P1.uid OR PF1.pid=P1.pid LEFT JOIN blocks AS B ON P1.pid=B.pid LEFT JOIN announcements AS A1 ON A1.pid=P1.pid LEFT JOIN notes AS N ON N.pid=P1.pid LEFT JOIN projectfollows AS PF2 ON PF2.pid=P1.pid JOIN users AS U2 ON P1.uid=U2.uid WHERE U1.uid=%s GROUP BY P1.pid, U1.uid, U2.uid ORDER BY paddtime DESC LIMIT %s"
        cur.execute(sql, (current_user.id,plimit))
        res = cur.fetchall()
        projects = res

    else: 
        sql = "SELECT A1.aid AS aid, A1.title AS title, A1.addtime AS aaddtime, U2.uid AS uid, P1.pid AS pid, P1.pname AS pname, U2.username AS username FROM announcements AS A1, projects AS P1, users AS U2 WHERE A1.pid = P1.pid AND U2.uid=P1.uid ORDER BY aaddtime DESC LIMIT %s"
        cur.execute(sql, (alimit,))
        res = cur.fetchall()
        announcements = res

        sql =  "SELECT P1.pid AS pid, P1.pname AS pname, P1.addtime AS paddtime, P1.uid AS uid, U.username AS username, COUNT(DISTINCT B.bid) AS blocks_count, COUNT(DISTINCT A1.aid) AS announcements_count, COUNT(DISTINCT N.nid) AS notes_count, COUNT(DISTINCT PF.uid) AS follower_count FROM projects AS P1 JOIN users AS U ON U.uid=P1.uid LEFT JOIN blocks AS B ON P1.pid=B.pid LEFT JOIN announcements AS A1 ON A1.pid=P1.pid LEFT JOIN notes AS N ON N.pid=P1.pid LEFT JOIN projectfollows AS PF ON PF.pid=P1.pid GROUP BY P1.pid, U.uid ORDER BY paddtime DESC LIMIT %s"
        cur.execute(sql, (plimit,))
        res = cur.fetchall()
        projects = res



    return render_template('feed.html', title = "We, Writers", alimit = alimit, plimit = plimit, projects=projects, announcements = announcements)


@main.route('/note',  strict_slashes=False)
@main.route('/note/<nid>/')
def note(nid=None):
    try:
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
        cur.execute(sql, (nid,))
        res = cur.fetchall()
        note['tags'] = res

        # get user info
        sql = "SELECT username FROM users WHERE uid = %s"
        cur.execute(sql, (uid,))
        res = cur.fetchone()
        user = {'uid': uid, 'uname': res['username']}

        # get project info
        sql = "SELECT pname FROM projects WHERE pid = %s"
        cur.execute(sql, (pid,))
        res = cur.fetchone()
        project = {'pid': pid, 'pname': res['pname']}

        # get replies info
        sql = "SELECT R.rid AS rid, R.text AS rtext, R.addtime AS raddtime, U.uid AS ruid, U.username AS runame FROM replies AS R, users as U WHERE R.nid = %s AND R.uid = U.uid ORDER BY raddtime ASC"
        cur.execute(sql, (nid,))
        res = cur.fetchall()
        replies = res
    except Exception as e:
        print(e)
        flash("Selected note doesn't exist. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))


    return render_template('note.html', title = "Note #" + str(note['nid']) + ": "+str(note['ntitle']), hide = True, note = note, user = user, project = project, replies = replies)

@main.route('/project', strict_slashes=False)
@main.route('/project/<pid>/')
def project(pid=None):

    try:

        if pid == None:
            flash("No project selected, redirected to all projects.", category="error")


        con = get_db() # gets the connection, need figure out the connection close
        cur = con.cursor() # get cursor for connection

        if request.args.get("follow") == 'toggle' and current_user.is_authenticated:
            sql = "SELECT * FROM projectfollows WHERE pid = %s AND uid = %s"
            cur.execute(sql,(pid,current_user.id))
            if cur.fetchone() == None:
                sql = "INSERT INTO projectfollows (pid, uid) VALUES (%s, %s)"
            else:
                sql = "DELETE FROM projectfollows WHERE pid = %s AND uid = %s"
            cur.execute(sql, (pid,current_user.id))
            con.commit()

        

            
        # following
        follows = False
        if current_user.is_authenticated:
            sql = "SELECT * FROM projectfollows WHERE pid = %s AND uid = %s"
            cur.execute(sql,(pid,current_user.id))
            if cur.fetchone() != None:
                follows = True

        sql = "SELECT P.pid AS pid, U.uid AS uid, P.pname AS pname, U.username AS username, P.description AS pdescription, P.addTime AS paddtime FROM Projects as P, Users as U WHERE U.uid = P.uid AND P.pid=%s" # query
        cur.execute(sql, (pid,))
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



    except Exception as e:
        print(e)
        flash("Selected project doesn't exist. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))

    return render_template('project.html', title = "Project #"+ str(project['pid']) + ": "+str(project['pname']), hide = True, project = project, categories = categories, blocks = blocks, bcount = bcount, announcements = announcements, acount = acount, notes = notes, ncount = ncount, follows = follows)

@main.route('/announcement', strict_slashes=False)    
@main.route('/announcement/<aid>/')
def announcement(aid=None):

    try:

        if aid == None:
            flash("No announcement selected, redirected to main page.", category="error")
            return redirect(url_for("main.index"))


        con = get_db() # gets the connection, need figure out the connection close
        cur = con.cursor() # get cursor for connection


        sql = "SELECT A.aid AS aid, A.title AS atitle, A.text AS atext, A.addtime AS aaddtime, P.pid AS pid, P.pname AS pname, U.uid AS uid, U.username AS username FROM announcements AS A, projects AS P, users AS U WHERE A.aid=%s AND A.pid=P.pid AND P.uid=U.uid" # query
        cur.execute(sql, (aid,))
        res = cur.fetchone()
        announcement = res
        return render_template('announcement.html', title = "Announcement #" + str(announcement['aid']) + ": "+str(announcement['atitle']), hide = True, announcement = announcement)

    except Exception as e:
        print(e)
        flash("Selected announcement doesn't exist. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))

    return render_template('announcement.html', title = "Announcement #" + str(announcement['aid']) + ": "+str(announcement['atitle']), hide = True, announcement = announcement)    
    
    
@main.route('/block', strict_slashes=False)
@main.route('/block/<bid>/')
def block(bid=None):

    try:

        if bid == None:
            flash("No block selected, redirected to main page.", category="error")
            return redirect(url_for("main.index"))


        con = get_db() # gets the connection, need figure out the connection close
        cur = con.cursor() # get cursor for connection


        sql = "SELECT B.bid AS bid, B.title AS btitle, B.addtime AS baddtime, B.text AS btext, U.uid AS uid, U.username AS username, P.pid AS pid, P.pname AS pname FROM blocks AS B, users AS U, projects AS P WHERE U.uid=P.uid AND P.pid=B.pid AND B.bid=%s" # query
        cur.execute(sql, (bid,))
        res = cur.fetchone()
        block = res
    except Exception as e:
        print(e)
        flash("Selected block doesn't exist. Redirected to all projects.", category="error")
        return redirect(url_for("main.projects"))


    return render_template('block.html', title = "Block #" + str(block['bid']) + ": "+str(block['btitle']), hide = True, block = block)

@main.route('/user', strict_slashes=False)
@main.route('/user/<uid>/')
def user(uid=None):

    try:

        if uid == None:
            flash("No user selected, redirected to all users.", category="error")
            return redirect(url_for("main.users"))


        con = get_db() # gets the connection, need figure out the connection close
        cur = con.cursor() # get cursor for connection


        sql = "SELECT uid, username, regtime FROM users WHERE uid=%s" # query
        cur.execute(sql, (uid,))
        res = cur.fetchone()
        user = res
        sql = "SELECT P.pid AS pid, P.pname AS pname, P.addtime AS paddtime FROM projects AS P WHERE P.uid=%s" # query
        cur.execute(sql, (uid,))
        res = cur.fetchall()
        projects = res
        projects_length = len(projects)
        sql = "SELECT P.pid AS pid, P.pname AS pname, P.addtime AS paddtime FROM projects AS P, projectfollows AS PF WHERE P.pid=PF.pid AND PF.uid=%s" # query
        cur.execute(sql, (uid,))
        res = cur.fetchall()
        followed = res
        followed_length = len(followed)
        sql = "SELECT P.pid AS pid, P.pname AS pname, N.nid AS nid, N.title AS ntitle, N.addtime AS naddtime FROM projects AS P, notes AS N WHERE P.pid=N.pid AND N.uid=%s" # query
        cur.execute(sql, (uid,))
        res = cur.fetchall()
        notes = res
        notes_length = len(notes)
    except Exception as e:
        print(e)
        flash("Selected user doesn't exist. Redirected to all users.", category="error")
        return redirect(url_for("main.users"))

    
    return render_template('user.html', title = "User #" + str(user['uid']) + ": "+str(user['username']), hide = True, user=user, projects=projects, projects_length=projects_length, followed=followed, followed_length=followed_length, notes=notes, notes_length=notes_length)


@main.route('/users/')
def users():

    limit = 10
    term = request.args.get("search")
    search = term

    p = request.args.get("p")

    if p != None:
        limit = int(p) + 10

    con = get_db()
    cur = con.cursor()



    res = []

    if term != None:

        sql = "SELECT U.uid AS uid, U.username AS username, U.regtime AS regtime, COUNT(DISTINCT P1.pid) AS project_count, COUNT(DISTINCT N.nid) AS note_count, COUNT(PF.uid) AS follow_count, COUNT(DISTINCT PF.uid) AS follower_count FROM users AS U LEFT JOIN projects AS P1 ON P1.uid=U.uid LEFT JOIN notes AS N ON P1.pid=N.nid LEFT JOIN projectfollows AS PF ON PF.pid=P1.pid WHERE username LIKE %(like)s ESCAPE '=' GROUP BY U.uid ORDER BY regtime DESC LIMIT %(limit)s"

        term = term.replace('=', '==').replace('%', '=%').replace('_', '=_')

        cur.execute(sql, dict(like='%'+term+'%', limit=limit, ))
        res = cur.fetchall()

    else:
        sql = "SELECT U.uid AS uid, U.username AS username, U.regtime AS regtime, COUNT(DISTINCT P1.pid) AS project_count, COUNT(DISTINCT N.nid) AS note_count, COUNT(PF.uid) AS follow_count, COUNT(DISTINCT PF.uid) AS follower_count FROM users AS U LEFT JOIN projects AS P1 ON P1.uid=U.uid LEFT JOIN notes AS N ON P1.pid=N.nid LEFT JOIN projectfollows AS PF ON PF.pid=P1.pid GROUP BY U.uid ORDER BY regtime DESC LIMIT %s"
        cur.execute(sql, (limit,))

        res = cur.fetchall()


    return render_template('search-user.html', title="User Search",  limit = limit, users=res, search = search)

@main.route('/projects/')
def projects():
    limit = 10
    term = request.args.get("search")
    search = term

    p = request.args.get("p")

    if p != None:
        limit = int(p) + 10

    con = get_db()
    cur = con.cursor()

    


    res = []

    if term != None:

        sql = "SELECT P1.pid AS pid, P1.pname AS pname, P1.addtime AS paddtime, P1.uid AS uid, U.username AS username, COUNT(DISTINCT B.bid) AS blocks_count, COUNT(DISTINCT A1.aid) AS announcements_count, COUNT(DISTINCT N.nid) AS notes_count, COUNT(DISTINCT PF.uid) AS follower_count FROM projects AS P1 JOIN users AS U ON U.uid=P1.uid LEFT JOIN blocks AS B ON P1.pid=B.pid LEFT JOIN announcements AS A1 ON A1.pid=P1.pid LEFT JOIN notes AS N ON N.pid=P1.pid LEFT JOIN projectfollows AS PF ON PF.pid=P1.pid WHERE pname LIKE %(like)s ESCAPE '=' GROUP BY P1.pid, U.uid ORDER BY paddtime DESC LIMIT %(limit)s"

        term = term.replace('=', '==').replace('%', '=%').replace('_', '=_')

        cur.execute(sql, dict(like='%'+term+'%', limit=limit,))
        res = cur.fetchall()


    else:
        sql = "SELECT P1.pid AS pid, P1.pname AS pname, P1.addtime AS paddtime, P1.uid AS uid, U.username AS username, COUNT(DISTINCT B.bid) AS blocks_count, COUNT(DISTINCT A1.aid) AS announcements_count, COUNT(DISTINCT N.nid) AS notes_count, COUNT(DISTINCT PF.uid) AS follower_count FROM projects AS P1 JOIN users AS U ON U.uid=P1.uid LEFT JOIN blocks AS B ON P1.pid=B.pid LEFT JOIN announcements AS A1 ON A1.pid=P1.pid LEFT JOIN notes AS N ON N.pid=P1.pid LEFT JOIN projectfollows AS PF ON PF.pid=P1.pid GROUP BY P1.pid, U.uid ORDER BY paddtime DESC LIMIT %s"
        cur.execute(sql, (limit,))

        res = cur.fetchall()


    return render_template('search-project.html', title="Project Search",  limit = limit, projects=res, search = search)