from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
from wtforms.widgets import PasswordInput


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    user_handle = StringField("User Handle", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class PostForm(FlaskForm):
    content = StringField("Content", validators=[DataRequired()])
    submit_button = SubmitField("Submit")
