import os
import file_db

def scan(localhost, backup_name, db):
    backup_info = db.get_backup_info(localhost, backup_name)
    print(backup_info)
    #for (root, dirs, files) in os.walk(backup_root):
     #   for f in files:
      #      db.get_entry(file_db.FileDB.make_path(backup_name, os.path.join(root, f)))
