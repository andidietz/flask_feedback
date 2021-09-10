from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

class LoginForm(FlaskForm):
    """ Login Form """

    username = StringField('Username')
    password = PasswordField('Password')

class RegisterForm(FlaskForm):
    """ Register Form """

    username = StringField('Username')
    password = PasswordField('Password')
    email = StringField('email')
    first_name = StringField('First Name')
    last_name = StringField('Last Name')

class FeedbackForm(FlaskForm):
    """ Add and Edit Feedback Form """
    
    title = StringField('Tilte')
    content = StringField('content')