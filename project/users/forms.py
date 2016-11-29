from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, \
    SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class RegisterForm(FlaskForm):
    id = IntegerField()
    name = StringField(
        'Username',
        validators=[DataRequired(), Length(min=6, max=25)])
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=25)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(),
                                                           EqualTo('password',
                                                                   message='Passwords must match')]
                            )


class LoginForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
