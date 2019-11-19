import binascii
import hashlib
import os


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
            authentication_method = 'cleartext'
        # See comment in UserManager.add_user about authentication_method.
        if authentication_method == 'hash':
            result = check_hashed_password(password, self.get('hash'))
        elif authentication_method == 'cleartext':
            result = (self.get('password') == password)
        else:
            raise NotImplementedError(authentication_method)
        return result


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
