import sqlite3
import os

class FileDB:
    """description of class"""
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def __init__(self, db_file):
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.create_db()

    def create_db(self):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('''CREATE TABLE backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host TEXT,
                name TEXT,
                local_root_path TEXT,
                last_update DATETIME
                )''')
            c.execute('''CREATE TABLE local_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_id INTEGER,
                local_path TEXT,
                backup_file_id INTEGER
                )''')
            c.execute('''CREATE TABLE backup_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_id INTEGER,
                backup_storage_path TEXT,
                update_time DATETIME,
                digest TEXT,
                hard_links INTEGER
                )''')
            db.commit()

    def add_backup(self, localhost, backup_name, local_path):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('INSERT INTO backups (host, name, local_root_path) VALUES (?, ?, ?)', (localhost, backup_name, local_path))
            db.commit()

    def get_backup_info(self, localhost, backup_name):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.row_factory = FileDB.dict_factory
            c.execute('''SELECT * FROM backups WHERE name = ?''', (backup_name,))
            results = c.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise RuntimeError('Expected single result')

    def get_local_file(self, backup_id, local_path = None, backup_file_id = None):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.row_factory = FileDB.dict_factory
            if local_path:
                c.execute('''SELECT * FROM local_files WHERE local_path = ? AND backup_id = ?''', (local_path, backup_id))
            elif backup_file_id:
                c.execute('''SELECT * FROM local_files WHERE backup_file_id = ? AND backup_id = ?''', (backup_file_id, backup_id))
            else:
                raise RuntimeError('') # throw something interesting, or handle this case
            results = c.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise RuntimeError('Expected single result')
    
    def get_backup_file(self, id):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('''SELECT * FROM backup_files WHERE id = ?''', (id,))
            c.row_factory = FileDB.dict_factory
            results = c.fetchall()
            if len(results) == 0:
                return None
            elif len(results) == 1:
                return results[0]
            else:
                raise RuntimeError('Expected single result')

    def get_backup_files(self, backup_id):
        with sqlite3.connect(self.db_file) as db:
            c = db.cursor()
            c.execute('''SELECT * FROM backup_files WHERE backup_id = ?''', (backup_id,))
            c.row_factory = FileDB.dict_factory
            return c.fetchall()
