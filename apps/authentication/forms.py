# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, FileField,StringField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import Email, DataRequired

# login and registration


class LoginForm(FlaskForm):
    username = TextField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = TextField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    photo = FileField('Your photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'JPEG'], 'Images only!')
    ])
    #{'user', 'docter', 'worker', 'teacher'}
    role = SelectField('Role',
                             id='role_create',
                             choices=[ 
                             ('student', 'student'),
                             ('teacher', 'teacher'),
                             ])
class EditAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = StringField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    role = SelectField('Role',
                             id='role_create',
                             choices=[ 
                             ('student', 'student'),
                             ('teacher', 'teacher'),
                             ])