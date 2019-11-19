import users


class UserManager(object):
    """A very simple user Manager, that saves it's data as json."""

    def __init__(self):
        self.database = users.Users()

    def read(self):
        return self.get_all_users()

    def get_all_users(self):
        return self.database.get_all_users()

    # def write(self, data):
    #     with open(self.file, 'w') as f:
    #         f.write(json.dumps(data, indent=2))

    def login_user(self, username, password):
        return self.database.login_user(username, password)

    def add_user(self, name, password,
                 active=True, roles=[], authentication_method='cleartext'):
        if authentication_method == 'hash':
            password = users.make_salted_hash(password)
        else:
            password = password

        data = {
            'name': name,
            'password': password,
            'active': active,
            'authentication_method': authentication_method,
            'authenticated': False
        }
        return self.database.save_user(users.User(self, 0, data))

    def get_user(self, user_id):
        return self.database.get_user(user_id)

    def delete_user(self, user_id):
        return self.database.remove_user(user_id)

    def update(self, user_id, userdata):
        return self.database.save(users.User(self, user_id, userdata))
