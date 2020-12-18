from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(max=32)])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(max=32)])
    submit = SubmitField('Log in')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=32)])
    email = StringField('Email', validators=[DataRequired(), Length(max=128), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=32)])
    password2 = PasswordField('Repeat password', validators=[
        DataRequired(), Length(max=32), EqualTo('password', 'Both passwords must match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PostForm(FlaskForm):
    text = TextAreaField('Message', validators=[
        DataRequired(), Length(max=512)
    ])
    submit = SubmitField('Save')

class ConfirmDelete(FlaskForm):
    submit = SubmitField('Delete')