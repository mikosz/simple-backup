import unittest
import file_db
import scanner
import tempfile
import os
import shutil
import logging

class Test_scanner_test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.INFO)

        self.tmpdir = tempfile.mkdtemp()
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        return super().tearDown()

    def test_A(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        db.add_backup('local', 'test_backup', 'f:\\private')
        changes = scanner.scan('local', 'test_backup', db)
        print(changes)

if __name__ == '__main__':
    unittest.main()
