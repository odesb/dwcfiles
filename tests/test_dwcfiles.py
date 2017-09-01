import os
import dwcfiles
import unittest
import tempfile

class DwcfilesTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, dwcfiles.app.config['DATABASE'] = tempfile.mkstemp()
        dwcfiles.app.testing = True
        self.app = dwcfiles.app.test_client()
        with dwcfiles.app.app_context():
            dwcfiles.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(dwcfiles.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()
