"""
    Forms
    ~~~~~
"""
from flask_login import current_user
from flask_wtf import Form
from wtforms import BooleanField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError
from wtforms import StringField

from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users


class URLForm(Form):
    url = TextField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(Form):
    term = TextField('', [InputRequired()])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(Form):
    title = TextField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = TextField('')


class UserEditorForm(Form):
    name = StringField("Name", [InputRequired()])
    password = StringField("Password", [InputRequired()])
    active = BooleanField("Active", default=False)


class LoginForm(Form):
    name = TextField('', [InputRequired()])
    password = PasswordField('', [InputRequired()])

    def validate_name(form, field):
        user = current_users.get_user(field.data)
        if not user:
            raise ValidationError('This username does not exist.')

    def validate_password(form, field):
        user = current_users.get_user(form.name.data)
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError('Username and password do not match.')


class ChangePasswordForm(Form):
    old_password = PasswordField('', [InputRequired()])
    new_password = PasswordField('', [InputRequired()])
    confirm_password = PasswordField('', [InputRequired()])

    def validate_confirm_password(form, field):
        password = form.new_password.data
        confirm_password = field.data
        if password != confirm_password:
            raise ValidationError('New password must match.')

    def validate_old_password(form, field):
        user = current_user
        if not user:
            return
        if not user.check_password(field.data):
            raise ValidationError('Your password is incorrect.')