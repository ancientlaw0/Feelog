from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,Length
import sqlalchemy as sa
from app import db
from app.models import User
from flask import current_app

class LoginForm(FlaskForm):
    username = StringField('Username' , validators=[DataRequired()])
    password = PasswordField('Password' , validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username' , validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8,message='Password must be 8 characters long')])
    password2 = PasswordField('Rewrite Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')


    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))   

        if user is not None:
                raise ValidationError('Please use a different email address.')
        else:
            allowed = current_app.config['ALLOWED_DOMAINS']
            
            domain = email.data.split('@')[-1].lower()              # Adding domain validation to avoid spam mails
            if domain not in allowed and not domain.endswith(('ac.in', 'edu.in')):
                raise ValidationError("Please try to choose other domain")
        
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match. Please try again.')])
    submit = SubmitField('Request Password Reset')