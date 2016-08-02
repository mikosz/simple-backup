import os
import file_db
import hashlib
import logging

def digest(path):
    m = hashlib.md5()
    with open(path, 'rb') as f:
        d = f.read(1024)
        while d:
            m.update(d)
            d = f.read(1024)
    return m.digest()

class ScanResult:

    class FileEntry:

        def __init__(self, backup_id, local_path, update_time = None, digest = None):
            self.backup_id = backup_id
            self.local_path = local_path
            self.update_time = update_time
            self.digest = digest

    def __init__(self):
        self.added = []
        self.modified = []
        self.removed = []

def scan(localhost, backup_name, db):
    result = ScanResult()

    backup_info = db.get_backup_info(localhost, backup_name)
    backup_id = backup_info['id']
    backup_root = backup_info['local_root_path']

    logging.info('Scanning directory backup %s at %s', backup_name, backup_root)

    for (root, dirs, files) in os.walk(backup_root):
        for f in files:
            local_file_entry = db.get_local_file(backup_id, local_path=f)
            direct_path = os.path.join(root, f)
            update_time = os.path.getmtime(direct_path)
            if local_file_entry == None:
                file_digest = digest(direct_path)
                local_path = os.path.relpath(direct_path, backup_root).replace('\\', '/')
                entry = ScanResult.FileEntry(backup_id, local_path, update_time, file_digest)
                result.added.append(entry)
                logging.info('-- found new file: %s', vars(entry))
            else:
                backup_file_id = local_file_entry['backup_file_id']
                backup_file = db.get_backup_file(backup_file_id)
                backup_file_update_time = backup_file['update_time']
                backup_file_digest = backup_file['digest']
                backup_file_hard_links = backup_file['hard_links']

                if update_time > backup_file_update_time:
                    file_digest = digest(local_path)
                    if file_digest != backup_file_digest:
                        result.modified.append(ScanResult.FileEntry(backup_id, f, update_time, digest))

    backup_files = db.get_backup_files(backup_id)
    for backup_file in backup_files:
        local_file = db.get_local_file(backup_id, backup_file_id=backup_file_id)
        local_path = backup_file['local_path']
        backup_file_update_time = backup_file['update_time']
        backup_file_digest = backup_file['digest']

        if not os.path.exists(os.path.join(backup_root, local_path)):
            result.removed.append(ScanResult.FileEntry(backup_id, local_path, backup_file_update_time, backup_file_digest))

    return result
