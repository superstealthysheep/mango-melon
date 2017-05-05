import os

import models
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import ValidationError, DataRequired, regexp, Email, EqualTo, Length


def username_exists(form, field):
    try:
        models.User.get(models.User.username ** field.data)
    except models.DoesNotExist:
        pass
    else:
        raise ValidationError('User with that username already exists')


def email_exists(form, field):
    try:
        models.User.get(models.User.email ** field.data)
    except models.DoesNotExist:
        pass
    else:
        raise ValidationError('User with that email already exists')

class SignUpForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            username_exists,
            regexp(r'^[a-z0-9]{3,10}$', message='Username can only be lowercase letters and numbers and length can only be 3-10 characters long')
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

"""
# New security feature: pre-shared key.

 - Need key to Signup
 - Key is in os.environ or Heroku environment vars

Forms model below:

    tdic_key = StringField(
    'Pre-Shared Key'
    validators=[
        DataRequired()
        EqualTo(os.environ('tdic_key'), message='Must use correct pre-shared key')
    ]
    )
"""
class SignInForm(Form):
    name_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class PostForm(Form):
    content = TextAreaField('What do you have to say?', validators=[Length(1, 255)])
