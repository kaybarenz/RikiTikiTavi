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

def get_default_authentication_method():
    return current_app.config.get('DEFAULT_AUTHENTICATION_METHOD', 'cleartext')

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





