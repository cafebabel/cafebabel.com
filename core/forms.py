from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class UserForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    firstname = StringField('firstname', validators=[DataRequired()])
    firstname = StringField('firstname', validators=[DataRequired()])
