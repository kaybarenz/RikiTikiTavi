"""
    User classes & helpers
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import os
import json
import binascii
import hashlib
from functools import wraps

from flask import current_app
from flask_login import current_user

from users.users import Users


class UserManager(object):
    """A very simple user Manager, that saves it's data as json."""

    def __init__(self):
        self.database = Users()

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
            password = make_salted_hash(password)
        else:
            password = password

        data = {
            'name': name,
            'password': password,
            'active': active,
            'authentication_method': authentication_method,
            'authenticated': False
        }
        return self.database.save_user(User(self, 0, data))

    def get_user(self, user_id):
        return self.database.get_user(user_id)

    def delete_user(self, user_id):
        return self.database.remove_user(user_id)

    def update(self, user_id, userdata):
        return self.database.save(User(self, user_id, userdata))


class User(object):
    def __init__(self, manager, user_id, data):
        self.manager = manager
        self.id = user_id
        self.data = data

    def get(self, option):
        return self.data.get(option)

    def set(self, option, value):
        self.data[option] = value

    def set_password(self, password):
        if self.get('authentication_method') == 'hash':
            self.set('password', make_salted_hash(password))
        else:
            self.set('password', password)
        self.save()

    def save(self):
        self.manager.save_user(self)

    def is_authenticated(self):
        return self.data.get('authenticated')

    def is_active(self):
        return self.data.get('active')

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def has_role(self, role):
        return role.lower() in (r.lower() for r in self.data.get('roles'))

    def check_password(self, password):
        """Return True, return False, or raise NotImplementedError if the
        authentication_method is missing or unknown."""
        authentication_method = self.data.get('authentication_method', None)
        if authentication_method is None:
            authentication_method = get_default_authentication_method()
        # See comment in UserManager.add_user about authentication_method.
        if authentication_method == 'hash':
            result = check_hashed_password(password, self.get('hash'))
        elif authentication_method == 'cleartext':
            result = (self.get('password') == password)
        else:
            raise NotImplementedError(authentication_method)
        return result


def get_default_authentication_method():
    return current_app.config.get('DEFAULT_AUTHENTICATION_METHOD', 'cleartext')


def make_salted_hash(password, salt=None):
    if not salt:
        salt = os.urandom(64)
    d = hashlib.sha512()
    d.update(salt[:32])
    d.update(password)
    d.update(salt[32:])
    return binascii.hexlify(salt) + d.hexdigest()


def check_hashed_password(password, salted_hash):
    salt = binascii.unhexlify(salted_hash[:128])
    return make_salted_hash(password, salt) == salted_hash


def protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_app.config.get('PRIVATE') and not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return wrapper


def admin_protect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_app.config.get('PRIVATE') and \
                (not current_user.is_authenticated or not current_user.has_role('admin')):
            return current_app.login_manager.unauthorized()
        return f(*args, **kwargs)

    return wrapper
