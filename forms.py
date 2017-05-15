import os

import models
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, FileField
from wtforms.validators import ValidationError, DataRequired, regexp, Email, EqualTo, Length
from flask_bcrypt import check_password_hash

if 'HEROKU' in os.environ:
    AUTH_PASS = os.environ['auth_pass']
else:
    AUTH_PASS = 'gjdfskghl'


def username_exists(form, field):
    print(form)
    try:
        models.User.get(models.User.username ** field.data)
    except models.DoesNotExist:
        pass
    else:
        raise ValidationError('User with that username already exists')


def email_exists(form, field):
    print(form)
    try:
        models.User.get(models.User.email ** field.data)
    except models.DoesNotExist:
        pass
    else:
        raise ValidationError('User with that email already exists')


def auth_matches(form, field):
    print(form)
    if check_password_hash(AUTH_PASS, field.data):
        pass
    else:
        raise ValidationError('Special password incorrect')


class SignUpForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            username_exists,
            regexp(r'^[a-z0-9]{3,10}$',
                   message='Username can only be lowercase letters & numbers, '
                           'and length can only be 3-10 characters long')
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            email_exists,
            Email()
        ]
    )
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(),
            regexp(r'[A-Z][a-z]+', message='Name can only be uppercase first letter and lowercase proceeding letters')
        ]
    )
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(),
            regexp(r'[A-Z][a-z]+', message='Name can only be uppercase first letter and lowercase proceeding letters')
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            EqualTo('password2', message='Passwords must match'),
        ]
    )
    password2 = PasswordField(
        'Confirm Password',
        validators=[DataRequired()]
    )

    auth = PasswordField(
        'Special Password',
        validators=[
            DataRequired(),
            auth_matches
        ]
    )


class SignInForm(Form):
    name_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class PostForm(Form):
    content = FileField()

