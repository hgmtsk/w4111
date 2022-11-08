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
        # TODO: IMPORTANT HERE - need to return no record or something
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

    sql = "SELECT pid, U.uid, pname,username, description, P.addTime FROM Projects as P, Users as U WHERE U.uid = P.uid AND P.pid={}".format(pid) # query
    
    cur = con.cursor() # get cursor for connection

    cur.execute(sql) 

    author = cur.fetchall()

    sql = "SELECT cname FROM projects, projectcategories, categories WHERE projects.pid={} AND projects.pid=projectcategories.pid AND projectcategories.cid=categories.cid".format(pid) # query

    cur.execute(sql) 

    pcategories = cur.fetchall()

    sql = "SELECT bid, title, addtime FROM blocks WHERE pid={}".format(pid) # query

    cur.execute(sql) 

    pblocks = cur.fetchall()

    sql = "SELECT COUNT(*) AS blocks_count FROM blocks WHERE pid={}".format(pid) # query

    cur.execute(sql) 

    pblocks_count = cur.fetchall()

    sql = "SELECT aid, title, addtime FROM announcements WHERE pid={}".format(pid) # query

    cur.execute(sql) 

    pannouncements = cur.fetchall()

    sql = "SELECT COUNT(*) AS announcements_count FROM announcements WHERE pid={}".format(pid) # query

    cur.execute(sql) 

    pannouncements_count = cur.fetchall()

    sql = "SELECT notes.nid, notes.title, notes.addtime, users.username, notes.uid, tags.name, COUNT(rid) AS replies_count FROM notes, notetags, tags, replies, users WHERE notes.nid=notetags.nid AND notetags.tid=tags.tid AND users.uid=notes.uid AND notes.pid={} GROUP BY notes.nid, notes.title, notes.addtime, users.username, notes.uid, tags.name".format(pid) # query

    cur.execute(sql) 

    pnotes = cur.fetchall()

    sql = "SELECT COUNT(*) AS notes_count FROM notes WHERE pid={}".format(pid) # query

    cur.execute(sql) 

    notes_count = cur.fetchall()



    project_pid = author['pid']
    pname = author['pname']
    author_uid = author['U.uid']
    author_username = author['username']
    pdescription = author['description']
    addTime = author['P.addTime']


    categories = pcategories['cname']
    blocks = [] # {bid: xxx, title: yyy, addtime: vvv}
    for pblock in pblocks:
        block = [pblock['bid'],pblock['title'],pblock['addtime']]
        blocks.append(block)
    blocks_count = pblocks_count['blocks_count']
    announcements = [] # {aid: xxx, title: yyy, addtime: ccc}
    for pannouncement in pannouncements:
        announcement = [pannouncement['aid'],pannouncement['title'],pannouncement['addtime']]
        announcements.append(announcement)
    announcements_count = pannouncements_count['announcements_count']
    notes = [] # {nid: xxx, title: yyy, addtime: ccc, username: zzz, uid: ccc, tags: [x,y,z], replies_count}
    for pnote in pnotes:
        note = [pnote['notes.nid'],pnote['notes.title'],pnote['notes.addtime'],pnote['users.username'],pnote['notes.uid'],pnote['tags.name'],pnote['replies_count']]
        notes.append(note)
    notes_count = notes_count['notes_count']



    return render_template('project.html', title = "random", messages = block)
