from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, SubmitField,TextAreaField
from wtforms.validators import ValidationError, DataRequired
import sqlalchemy as sa
from app import db
from app.models import User
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed
from flask import request,current_app

class SearchForm(FlaskForm):
    q = StringField(('Search'), validators=[DataRequired()])

    # This form uses GET parameters instead of standard POST — so override formdata (search form)
    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}     # CSRF token doesn't make sense for GET requests (only for POST,PUT,DELETE)
        super(SearchForm, self).__init__(*args, **kwargs)

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    profile_image = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]) # with an error messgae at end 
    submit = SubmitField('Submit')
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username   # Used to allow same username editing

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError(('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

# Used for POST-based actions like follow/unfollow, just to enforce CSRF

class PostForm(FlaskForm):
    body= TextAreaField("What's on your mind?", validators=[DataRequired(),Length(min = 1, max = 200)])
    tag = SelectField('Tag', choices=[],default='')
    pic = FileField('Upload Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'media only!')])

    def __init__(self, *args, **kwargs): # toc access from config
        super().__init__(*args, **kwargs)
        self.tag.choices = current_app.config['TAG_CHOICES']  
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    comment_body = TextAreaField("share your views in the post", validators=[DataRequired(),Length(min=1,max=100)])
    submit = SubmitField('Submit')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField('Submit')