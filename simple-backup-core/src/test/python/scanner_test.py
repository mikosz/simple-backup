import unittest
import file_db
import scanner
import tempfile
import os
import shutil
import logging

class Test_scanner_test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.tmpdir = tempfile.mkdtemp(prefix='scanner_test_')
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        return super().tearDown()

    def test_works_when_backup_dir_missing(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        backup_dir = os.path.join(self.tmpdir, 'to_backup')
        db.add_backup('local', 'test_backup', backup_dir)
        changes = scanner.scan('local', 'test_backup', db)

        self.assertFalse(changes.added)
        self.assertFalse(changes.modified)
        self.assertFalse(changes.moved)
        self.assertFalse(changes.removed)

    def test_finds_new_files(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        backup_dir = os.path.join(self.tmpdir, 'to_backup')
        os.mkdir(backup_dir)
        backup_id = db.add_backup('local', 'test_backup', backup_dir)
        
        loose_file_local_path = 'loose-file.txt'
        loose_file_mtime = 42.123
        loose_file_digest = b'\xe8\x0bP\x17\t\x89P\xfcX\xaa\xd8<\x8c\x14\x97\x8e'
        loose_file_entry = scanner.ScanResult.FileEntry(backup_id, loose_file_local_path, update_time=loose_file_mtime, digest=loose_file_digest)

        loose_file_path = '%s/%s' % (backup_dir, loose_file_local_path)
        with open(loose_file_path, 'w') as loose:
            loose.write('abcdef')
        os.utime(loose_file_path, (0, loose_file_mtime))

        os.mkdir('%s/empty-subdir' % backup_dir)

        os.mkdir('%s/subdir' % backup_dir)

        file_in_subdir_local_path = 'subdir/file-in-subdir.txt'
        file_in_subdir_path = '%s/%s' % (backup_dir, file_in_subdir_local_path)
        file_in_subdir_mtime = 84.246
        file_in_subdir_digest = b'&\xe1b\xd0\xb5paA\xbd\xb9T\x90\n\xeb\xe8\x04'
        file_in_subdir_entry = scanner.ScanResult.FileEntry(backup_id, file_in_subdir_local_path, update_time=file_in_subdir_mtime, digest=file_in_subdir_digest)

        with open(file_in_subdir_path, 'w') as file_in_subdir:
            file_in_subdir.write('ghijkl')
        os.utime(file_in_subdir_path, (0, file_in_subdir_mtime))

        changes = scanner.scan('local', 'test_backup', db)        

        self.assertCountEqual(changes.added, [ loose_file_entry, file_in_subdir_entry ])
        self.assertCountEqual(changes.modified, [])
        self.assertCountEqual(changes.moved, [])
        self.assertCountEqual(changes.removed, [])

    def test_finds_modified_files(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        backup_dir = os.path.join(self.tmpdir, 'to_backup')
        os.mkdir(backup_dir)
        backup_id = db.add_backup('local', 'test_backup', backup_dir)

        loose_file_local_path = 'loose-file-touched-but-contents-same.txt'
        loose_file_mtime = 42.123
        loose_file_mtime_updated = loose_file_mtime + 3
        loose_file_digest = b'\xe8\x0bP\x17\t\x89P\xfcX\xaa\xd8<\x8c\x14\x97\x8e'
        loose_file_entry = scanner.ScanResult.FileEntry(backup_id, loose_file_local_path, update_time=loose_file_mtime_updated, digest=loose_file_digest)

        backup_file_id = db.add_backup_file(backup_id, '', loose_file_mtime, loose_file_digest)
        db.add_local_file(backup_id, loose_file_local_path, backup_file_id)

        loose_file_path = '%s/%s' % (backup_dir, loose_file_local_path)
        with open(loose_file_path, 'w') as loose:
            loose.write('abcdef')
        os.utime(loose_file_path, (0, loose_file_mtime_updated))

        os.mkdir('%s/empty-subdir' % backup_dir)

        os.mkdir('%s/subdir' % backup_dir)

        file_in_subdir_local_path = 'subdir/file-in-subdir-contents-changed.txt'
        file_in_subdir_path = '%s/%s' % (backup_dir, file_in_subdir_local_path)
        file_in_subdir_mtime = 84.246
        file_in_subdir_mtime_updated = 84.246 + 3
        file_in_subdir_digest = b'&\xe1b\xd0\xb5paA\xbd\xb9T\x90\n\xeb\xe8\x04'
        file_in_subdir_digest_updated = b'\xd2\xec\x9b2\xd6tAM\x11\x125>\xa8\x80w\x9b'
        file_in_subdir_entry = scanner.ScanResult.FileEntry(backup_id, file_in_subdir_local_path, update_time=file_in_subdir_mtime_updated, digest=file_in_subdir_digest_updated)

        backup_file_id = db.add_backup_file(backup_id, '', file_in_subdir_mtime, file_in_subdir_digest)
        db.add_local_file(backup_id, file_in_subdir_local_path, backup_file_id)

        with open(file_in_subdir_path, 'w') as file_in_subdir:
            file_in_subdir.write('ghijklmnop')
        os.utime(file_in_subdir_path, (0, file_in_subdir_mtime_updated))

        changes = scanner.scan('local', 'test_backup', db)        

        self.assertCountEqual(changes.added, [])
        self.assertCountEqual(changes.modified, [ file_in_subdir_entry ])
        self.assertCountEqual(changes.moved, [])
        self.assertCountEqual(changes.removed, [])

    def test_finds_moved_files(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        backup_dir = os.path.join(self.tmpdir, 'to_backup')
        os.mkdir(backup_dir)
        backup_id = db.add_backup('local', 'test_backup', backup_dir)
        
        loose_file_local_path = 'loose-file.txt'
        loose_file_moved_path = 'loose-file-moved.txt'
        loose_file_mtime = 42.123
        loose_file_digest = b'\xe8\x0bP\x17\t\x89P\xfcX\xaa\xd8<\x8c\x14\x97\x8e'
        loose_file_entry = scanner.ScanResult.FileEntry(backup_id, loose_file_moved_path, old_local_path=loose_file_local_path, update_time=loose_file_mtime, digest=loose_file_digest)

        backup_file_id = db.add_backup_file(backup_id, '', loose_file_mtime, loose_file_digest)
        db.add_local_file(backup_id, loose_file_local_path, backup_file_id)

        loose_file_path = '%s/%s' % (backup_dir, loose_file_moved_path)
        with open(loose_file_path, 'w') as loose:
            loose.write('abcdef')
        os.utime(loose_file_path, (0, loose_file_mtime))

        changes = scanner.scan('local', 'test_backup', db)        

        self.assertCountEqual(changes.added, [])
        self.assertCountEqual(changes.modified, [])
        self.assertCountEqual(changes.moved, [ loose_file_entry ])
        self.assertCountEqual(changes.removed, [])

    def test_finds_removed_files(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        backup_dir = os.path.join(self.tmpdir, 'to_backup')
        os.mkdir(backup_dir)
        backup_id = db.add_backup('local', 'test_backup', backup_dir)

        loose_file_local_path = 'loose-file.txt'
        loose_file_mtime = 0
        loose_file_digest = b''
        loose_file_entry = scanner.ScanResult.FileEntry(backup_id, loose_file_local_path, update_time=loose_file_mtime, digest=loose_file_digest)

        backup_file_id = db.add_backup_file(backup_id, '', loose_file_mtime, loose_file_digest)
        db.add_local_file(backup_id, loose_file_local_path, backup_file_id)

        changes = scanner.scan('local', 'test_backup', db)

        self.assertCountEqual(changes.added, [])
        self.assertCountEqual(changes.modified, [])
        self.assertCountEqual(changes.moved, [])
        self.assertCountEqual(changes.removed, [ loose_file_entry ])

if __name__ == '__main__':
    unittest.main()
