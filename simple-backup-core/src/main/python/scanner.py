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

        def __init__(self, backup_id, local_path, old_local_path = None, update_time = None, digest = None):
            self.backup_id = backup_id
            self.local_path = local_path
            self.old_local_path = old_local_path
            self.update_time = int(update_time)
            self.digest = digest

        def __lt__(self, other):
            return (self.backup_id, self.local_path, self.old_local_path, self.update_time, self.digest) < (other.backup_id, other.local_path, self.old_local_path, other.update_time, other.digest)

        def __eq__(self, other):
            return (self.backup_id, self.local_path, self.old_local_path, self.update_time, self.digest) == (other.backup_id, other.local_path, self.old_local_path, other.update_time, other.digest)

        def __hash__(self):
            return hash((self.backup_id, self.local_path, self.old_local_path, self.update_time, self.digest))

        def __str__(self):
            return str({ 'backup_id': self.backup_id, 'local_path': self.local_path, 'old_local_path': self.old_local_path, 'update_time': self.update_time, 'digest': self.digest })

    def __init__(self):
        self.added = []
        self.modified = []
        self.moved = []
        self.removed = []

def scan(localhost, backup_name, db):
    result = ScanResult()

    backup_info = db.get_backup_info(localhost, backup_name)
    backup_id = backup_info['id']
    backup_root = backup_info['local_root_path']

    added_files_by_digest = {}

    logging.info('Scanning directory backup %s at %s', backup_name, backup_root)

    for (root, dirs, files) in os.walk(backup_root):
        for f in files:
            absolute_path = os.path.join(root, f)
            local_path = os.path.relpath(absolute_path, backup_root).replace('\\', '/')

            local_file_entry = db.get_local_file(backup_id, local_path=local_path)

            # TODO: check update time and changes in size for quick modification check
            update_time = int(os.path.getmtime(absolute_path))

            if local_file_entry == None:
                file_digest = digest(absolute_path)
                entry = ScanResult.FileEntry(backup_id, local_path, update_time=update_time, digest=file_digest)
                result.added.append(entry)
                added_files_by_digest[file_digest] = entry
                logging.debug('-- found new file: %s', vars(entry))
            else:
                backup_file_id = local_file_entry['backup_file_id']
                backup_file = db.get_backup_file(backup_file_id)
                backup_file_update_time = backup_file['update_time']
                backup_file_digest = backup_file['digest']
                backup_file_hard_links = backup_file['hard_links']

                if update_time > backup_file_update_time:
                    file_digest = digest(absolute_path)
                    if file_digest != backup_file_digest:
                        entry = ScanResult.FileEntry(backup_id, local_path, update_time=update_time, digest=file_digest)
                        result.modified.append(entry)
                        logging.debug('-- found modified file: %s', vars(entry))

    backup_files = db.get_backup_files(backup_id)
    for backup_file in backup_files:
        backup_file_id = backup_file['id']
        backup_file_update_time = backup_file['update_time']
        backup_file_digest = backup_file['digest']

        local_file = db.get_local_file(backup_id, backup_file_id=backup_file_id)
        local_path = local_file['local_path']

        if not os.path.exists(os.path.join(backup_root, local_path)):
            moved = False
            for added_file in result.added:
                if added_file.digest == backup_file_digest:
                    result.added.remove(added_file)
                    moved_file = added_file
                    moved_file.old_local_path = local_path
                    result.moved.append(added_file)
                    moved = True
                    logging.debug('-- found moved file: %s', vars(moved_file))
            if not moved:
                entry = ScanResult.FileEntry(backup_id, local_path, update_time=backup_file_update_time, digest=backup_file_digest)
                result.removed.append(entry)
                logging.debug('-- removed file: %s', vars(entry))

    return result
