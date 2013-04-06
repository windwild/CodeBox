class database(object):
    """docstring for database"""


    def __init__(self, database, server = "localhost", username = "root", password = "root"):
        import MySQLdb as mdb
        self.server = server
        self.username = username
        self.password = password
        self.database = database
        con = mdb.connect(self.server ,self.username ,self.password ,self.database)
        self.cur = con.cursor()


    def connect():
        con = mdb.connect(self.server ,self.username ,self.password ,self.database)
        cur = con.cursor()
        return cur

    def select(self,sql,data=()):
        self.cur.execute(sql,data)
        results = self.cur.fetchall()
        return results

    def insert(self,sql,data=()):
        return self.run_sql(sql,data)

    def delete(self,sql,data=()):
        return self.run_sql(sql,data)

    def update(self,sql,data=()):
        return self.run_sql(sql,data)

    def run_sql(self,sql,data=()):
        info = self.cur.execute(sql)
        return info

