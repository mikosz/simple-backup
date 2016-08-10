import unittest
import file_db
import tempfile
import shutil
import os

class Test_file_db_test(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='db_test_')
        return super().setUp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        return super().tearDown()

    def test_creates_empty_db_if_not_exists(self):
        db_path = os.path.join(self.tmpdir, 'new-db')
        db = file_db.FileDB(db_path)
        self.assertTrue(os.path.exists(db_path))

if __name__ == '__main__':
    unittest.main()
