"""
    Connection to a User database
    ~~~~~~~~~~~~~~~~~~~~~~
"""

from users.user import User
import mysql.connector
import wiki


class Users(object):
    """Object acts like the database for Users."""

    def __init__(self):
        config = {
            'username': 'z4SjDxXsv4',
            'password': 'e6aHYGNvQw',
            'host': 'remotemysql.com',
            'database': 'z4SjDxXsv4'
        }
        self.connection = mysql.connector.connect(**config)

    def login_user(self, username, password):
        """Checks the user's username and password to see if its correct"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name = %s", (username,))

        result = cursor.fetchone()

        user = self.get_user(result[0])
        if user.get('authentication_method') == 'cleartext' and user.get('password') == password:
            return user
        elif user.get('authentication_method') == 'hash' and wiki.web.user.check_hashed_password(user.get('password'), password):
            return user
        else:
            return False

    def get_all_users(self):
        """Gets All users from the database"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")

        rows = cursor.fetchall()
        user_list = []
        for row in rows:
            data = {
                'name': row[1],
                'authentication_method': row[2],
                'password': row[3],
                'active': row[4],
                'authenticated': row[5],
                'roles': self.get_roles(row[0])
            }
            user_list.append(User(self, row[0], data))

        return user_list

    def get_user(self, user_id):
        """Gets a user from the database"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users where userID = %s", (user_id,))

        row = cursor.fetchone()
        if row:
            data = {
                'name': row[1],
                'authentication_method': row[2],
                'password': row[3],
                'active': row[4],
                'authenticated': row[5],
                'roles': self.get_roles(row[0])
            }
            return User(self, user_id, data)

    def save_user(self, user):
        """Creates or updates user from the database"""
        cursor = self.connection.cursor()
        if user.id == 0:
            cursor.execute(("INSERT INTO users "
                            "(name, authentication_method, password, active, authenticated) "
                            "VALUES (%s, %s, %s, %s, %s)"),
                           [user.get('name'), user.get('authentication_method'), user.get('password'),
                            user.get('active'), user.get('authenticated')])
            saved_user = user
            saved_user.id = cursor.lastrowid
        else:
            cursor.execute(
                """UPDATE users SET name=%s, authentication_method=%s, password=%s, active=%s, 
                authenticated=%s WHERE userID=%s""", (
                           user.get('name'), user.get('authentication_method'), user.get('password'),
                           user.get('active'), user.get('authenticated'), user.id))
            saved_user = user

        self.connection.commit()
        return saved_user

    def remove_user(self, user_id):
        """Removes User from database"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users WHERE userID = %s", (user_id,))
        self.connection.commit()
        return True

    def get_roles(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users_roles WHERE userID = %s", (user_id,))
        results = cursor.fetchall()
        roles = []
        for result in results:
            cursor.execute("SELECT * FROM roles WHERE roleID = %s", (result[2],))
            roles.append(cursor.fetchone()[1])
        return roles
