import sqlite3

class Database:
    def __init__(self,db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        
    def mahalla_kiritish(self,nomi,kenglik,uzunlik,rais,xojaliklar_soni):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'mahalla' (nomi,kenglik,uzunlik,rais,xojaliklar_soni) VALUES (?,?,?,?,?)",(nomi,kenglik,uzunlik,rais,xojaliklar_soni))

    def mahallalar_royxati(self):
        with self.connection:
            result =  self.cursor.execute("SELECT * FROM 'mahalla'").fetchall()
            return result