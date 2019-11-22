import os
from pathlib import Path

from wiki.web import create_app
import unittest


class TestPictures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        directory = Path(os.getcwd()).parent
        app = create_app(directory)
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_pictures_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/ajax/pictures')

        # assert the status code of the response
        # due to the way the system is set up, the result only has a redirect page instead of the route
        # that I wanted to test. I haven't been able to figure out how to get around that
        self.assertEqual(result.status_code, 200)
