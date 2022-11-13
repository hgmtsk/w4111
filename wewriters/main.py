from flask import Blueprint, render_template

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








    return render_template('feed.html', title = 'Main Page', messages = project)


@main.route('/note',  strict_slashes=False)
@main.route('/note/<nid>')
def note(nid=None):
    if nid == None:
        return 'no selected note'

    pid = 0
    uid = 0

    con = get_db()
    cur = con.cursor()

    # get note info
    sql = "SELECT pid, title, text, addtime, uid FROM notes WHERE nid = %s"
    if cur.execute(sql, (nid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something, redo try catch!!!!
        pass
    res = cur.fetchone()
    note = {'nid': nid, 'ntitle': res['title'], 'ntext': res['text'], 'naddtime': res['addtime'].replace(microsecond=0)}

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

@main.route('/project/')
def project():

    #later will be automatic:
    pid = 1


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    sql = "SELECT pid, U.uid, pname,username, description, P.addTime FROM Projects as P, Users as U WHERE U.uid = P.uid AND P.pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    author = {'pid': pid, 'uid': res['U.uid'], 'apname': res['pname'], 'ausername': res['username'], 'adescription': res['description'], 'aaddTime': res['P.addTime'].replace(microsecond=0)}

    sql = "SELECT cname FROM projects, projectcategories, categories WHERE projects.pid=%s AND projects.pid=projectcategories.pid AND projectcategories.cid=categories.cid" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    categories = {'cname': res['cname']}

    sql = "SELECT bid, title, addtime FROM blocks WHERE pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    blocks = {'bid': res['bid'], 'btitle': res['title'], 'baddtime': res['addtime']}

    sql = "SELECT COUNT(*) AS blocks_count FROM blocks WHERE pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    blocks_count = res['blocks_count']

    sql = "SELECT aid, title, addtime FROM announcements WHERE pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    announcements = {'aid': res['aid'], 'atitle': ['title'], 'aaddtime': res['addtime']}

    sql = "SELECT COUNT(*) AS announcements_count FROM announcements WHERE pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    announcements_count = res['announcements_count']

    sql = "SELECT notes.nid, notes.title, notes.addtime, users.username, notes.uid, tags.name, COUNT(rid) AS replies_count FROM notes, notetags, tags, replies, users WHERE notes.nid=notetags.nid AND notetags.tid=tags.tid AND users.uid=notes.uid AND notes.pid=%s GROUP BY notes.nid, notes.title, notes.addtime, users.username, notes.uid, tags.name" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    notes = {'nid': res['notes.nid'], 'ntitle': res['notes.title'], 'ausername': res['users.username'], 'nuid': res['notes.uid'], 'ntags': res['tags.name'], 'nreplies_count': res['replies_count']}

    sql = "SELECT COUNT(*) AS notes_count FROM notes WHERE pid=%s" # query
    if cur.execute(sql, (pid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    notes_count = res['notes_count']


    return render_template('project.html', title = "Project #" + ": "+str(project['ptitle']), hide = True, author = author, categories = categories, blocks = blocks, blocks_count = blocks_count, announcements = announcements, announcements_count = announcements_count, notes = notes, notes_count = notes_count)

    
@main.route('/announcements/')
def announcements():

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
    

@main.route('/block/')
def block():

    #later will be automatic:
    bid = 1


    con = get_db() # gets the connection, need figure out the connection close
    cur = con.cursor() # get cursor for connection


    sql = "SELECT B.bid, B.title, B.text, U.uid, U.username, P.pid, P.pname FROM blocks AS B, users AS U, people AS P WHERE U.uid=P.uid AND P.pid=B.pid AND B.bid=%s" # query
    if cur.execute(sql, (bid,)) != None:
        # TODO: IMPORTANT HERE - need to return no record or something
        pass
    res = cur.fetchall()
    blocks = {'bid': bid, 'btitle': res['B.title'], 'auid': res['U.uid'], 'busername': res['B.username'], 'bpid': res['P.pid'], 'bpname': ['P.pname']}

    return render_template('project.html', title = "Project #" + str(blocks['bid']) + ": "+str(blocks['btitle']), hide = True, blocks = blocks)

@main.route('/user/')
def user():

    #later will be automatic:
    uid = 1


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


    return render_template('users.html')

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