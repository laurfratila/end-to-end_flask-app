from dataclasses import field
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User
import re

def validate_password_strength(form, field):
    password = field.data or ""
    errors = []

    if len(password) < 12:
        errors.append(_("at least 12 characters"))

    if not re.search(r"[a-z]", password):
        errors.append(_("one lowercase letter (a–z)"))

    if not re.search(r"[A-Z]", password):
        errors.append(_("one uppercase letter (A–Z)"))

    if not re.search(r"[0-9]", password):
        errors.append(_("one digit (0–9)"))

    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:,.<>/?]", password):
        errors.append(_("one special character: !@#$%^&*()_-+=[]{};:,.<>/?"))

    if errors:
        raise ValidationError(
            _("Password must contain: ") + ", ".join(errors) + "."
        )


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(
    _l('Password'),
    validators=[DataRequired(), validate_password_strength]
)

    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
    _l('Password'),
    validators=[DataRequired(), validate_password_strength]
)

    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
