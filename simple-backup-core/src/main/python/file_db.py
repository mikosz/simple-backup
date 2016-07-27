import sqlite3
import os

class FileDB:
    """description of class"""
    
    def make_path(backup_name, path):
        return '//%s/%s' % (backup_name, path.replace('\\', '/'))

    def __init__(self, db_file):
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.create_db()

    def create_db(self):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('''CREATE TABLE backup_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT,
                backup_storage_path TEXT,
                update_time DATETIME,
                digest TEXT
                )''')
            c.execute('''CREATE TABLE backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                name TEXT,
                local_path TEXT,
                storage_path TEXT,
                last_update DATETIME
                )''')
            db.commit()

    def add_backup(self, localhost, backup_name, local_path):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('INSERT INTO backups (host, name, local_path) VALUES (?, ?, ?)', localhost, backup_name, local_path)
            db.commit()

    def get_backup_info(self, localhost, backup_name):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('''SELECT * FROM backups WHERE name = ?''', backup_name)
            results = c.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise RuntimeError('Expected single result')
