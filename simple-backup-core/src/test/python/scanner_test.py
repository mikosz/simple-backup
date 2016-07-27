import unittest
import file_db
import scanner
import tempfile
import os

class Test_scanner_test(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        return super().tearDown()

    def test_A(self):
        db = file_db.FileDB(os.path.join(self.tmpdir, 'test.db'))
        db.add_backup('local', 'test_backup', 'f:\\private')
        scanner.scan('local', 'test_backup', db)

if __name__ == '__main__':
    unittest.main()
