import unittest

from mysql.connector import MySQLConnection

from users import Users


class MyTestCase(unittest.TestCase):
    def test_init(self):
        self.assertIsInstance(Users().connection, MySQLConnection)


if __name__ == '__main__':
    unittest.main()
