import unittest

from mysql.connector import MySQLConnection

from users import Users, User, UserManager


class MyTestCase(unittest.TestCase):
    def test_init(self):
        self.assertIsInstance(Users().connection, MySQLConnection)

    def test_add_users(self):
        user_manager = UserManager()
        self.assertEqual('test', user_manager.add_user('test', 'password').get('name'))

    def test_get_user(self):
        user_manager = UserManager()
        self.assertEqual(11, user_manager.get_user(11).id)

    def test_delete_user(self):
        self.assertTrue(UserManager().delete_user(11))


if __name__ == '__main__':
    unittest.main()
