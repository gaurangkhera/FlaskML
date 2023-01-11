from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField, FileField, SelectField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Login")

class RegForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Length(min=4, max=64)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password',validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Register")

class UploadForm(FlaskForm):
    csv = FileField('Upload your CSV', validators=[FileRequired(), FileAllowed(['csv'])])
    sep = StringField('Seperator used in CSV', validators=[DataRequired()])
    submit = SubmitField('Upload')
