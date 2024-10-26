"""
This module contains DDL commands
Run it first time directly to create tables
"""

from typing_extensions import List
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from secrets import token_hex
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin
import matplotlib.pyplot as plt
import matplotlib.image as mpi
from eralchemy import render_er

app = Flask("Test_blog")  # create the app
app.secret_key = token_hex()  # a random session secret key
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # To prevent overhead
Bootstrap(app)  # to use bootstrap in html pages
ckeditor = CKEditor(app)  # to use a text editor in html pages


class Base(DeclarativeBase): ...  # some advanced config for db here if needed


# initialize the app with the extension
db = SQLAlchemy(app, model_class=Base)


class User(UserMixin, db.Model):  # a class represents a table
    id: Mapped[int] = mapped_column(primary_key=True)  # properties are columns
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    lastname: Mapped[str] = mapped_column(nullable=True)
    reg_date: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    # for convenience create a list of posts and comments for the user
    posts: Mapped[List["Post"]] = relationship(
        back_populates="author",  # back_populates the author in Post table with the user
        cascade="all, delete",  # if a user is deleted, all his stuff is deleted
    )
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="author",
        cascade="all, delete",
    )


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, nullable=False)
    content: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    # back_populates posts in User table with this post
    author = relationship("User", back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post",  # back_populates post in Comment table with this post
        cascade="all, delete",  # if a post is deleted, all its comments is deleted
    )


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(nullable=True)
    date: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey(User.id))
    author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(ForeignKey(Post.id))
    post: Mapped["Post"] = relationship(back_populates="comments")


if __name__ == "__main__":
    # perform the code below only if this file is started directly
    with app.app_context():  # db could be used only with app context
        # CREATE TABLE IF NOT EXISTS Table ();
        db.create_all()  # create the db file and all tables
        print("The DB file and tables have been created.")
        img = "model.png"
        render_er(db.metadata, img)
        plot = plt.imshow(mpi.imread(img))
        plt.rcParams["figure.figsize"] = (16, 10)
        plt.show()
