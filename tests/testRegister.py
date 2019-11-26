import unittest

import mysql.connector
from users import Users, User


class MyTestCase(unittest.TestCase):

    def test_email_used(self):
        test_email = "foxr@nku.edu"
        self.assertEqual(False, Users.email_used(test_email))

        test_email_two = "votop1@nku.edu"
        self.assertEqual(True, Users.email_used(test_email_two))

    def test_register_user(self):
        test_email = "wardb1@nku.edu"
        self.assertEqual(False, Users.email_used(emailAddress=test_email))

        test_name = "Ben"
        test_password = "Ward"
        Users.register_user(test_name, test_password, test_email)
        self.assertEqual(True, Users.email_used(emailAddress=test_email))

        Users.remove_user_by_email(test_email)
        self.assertEqual(False, Users.email_used(emailAddress=test_email))


if __name__ == '__main__':
    unittest.main()
