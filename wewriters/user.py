from flask_login import UserMixin

from wewriters.db import get_db

class User(UserMixin):
    def __init__(self, uid:str):
        self.id = uid
        self.uid = uid

        con = get_db()
        cur = con.cursor()
        sql = "SELECT username FROM Users WHERE uid = %s"
        cur.execute(sql,(self.id,))

        self.username = cur.fetchone()['username']

    
