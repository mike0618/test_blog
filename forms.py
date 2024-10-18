"""
This module contains flask forms for html templates
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
)
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField
from bleach import clean


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    password = PasswordField("Password", validators=[DataRequired(), Length(8)])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Enter")


class CommentForm(FlaskForm):
    text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Send")


class PersonalForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    lastname = StringField("Last Name")
    submit = SubmitField("Save")


class NewPassForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired(), Length(8)])
    password2 = PasswordField(
        "Repeat the password", validators=[DataRequired(), Length(8)]
    )
    submit = SubmitField("Save")


def clean_html(content):
    allowed_tags = {
        "a",
        "abbr",
        "acronym",
        "address",
        "b",
        "br",
        "dl",
        "dt",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "img",
        "li",
        "ol",
        "p",
        "pre",
        "q",
        "s",
        "small",
        "strike",
        "strong",
        "span",
        "sub",
        "sup",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "tt",
        "u",
        "ul",
    }
    allowed_attrs = {"a": ["href", "title"], "img": ["src", "alt"]}
    cleaned = clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return cleaned
