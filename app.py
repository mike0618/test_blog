"""
This module contains flask handling functions and DML commands
"""

from db_orm import db, app, User, Post, Comment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from flask import (
    render_template,
    send_from_directory,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
)
from forms import (
    clean_html,
    RegisterForm,
    LoginForm,
    CreatePostForm,
    CommentForm,
    PersonalForm,
)


# Current date and time
def date_time():
    return (datetime.now() + timedelta(hours=-7)).strftime("%m/%d/%Y, %I:%M:%S %p")


# Connect to LoginManager
login_manager = LoginManager()
login_manager.init_app(app)


# User Loader
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route("/")  # root web site url, by default used GET method
def home():
    posts = db.session.query(Post).all()  # SELECT * FROM Post;
    # send posts from DB to the template as all_posts
    return render_template("index.html", all_posts=posts)


@app.route("/favicon.ico")  # set web site icon
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


# this route works with GET and POST methods
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()  # use form from the forms module
    if form.validate_on_submit():  # when validated it comes via POST method
        username = form.username.data
        # check if username exists in the DB
        # SELECT * FROM User WHERE Username=username;
        if db.session.query(User).filter_by(username=username).first():
            flash("This account already exists. Try to login please.")
            # offer to try login if exists
            return redirect(url_for("login", username=username))
        user_hash = generate_password_hash(
            form.password.data, method="pbkdf2:sha256", salt_length=16
        )  # create pw hash
        new_user = User()  # create a user and save its columns
        # save the data from the form, hash and date
        new_user.username = username
        new_user.name = form.name.data
        new_user.lastname = form.lastname.data
        new_user.password = user_hash
        new_user.reg_date = date_time()
        # INSERT INTO User (columns) VALUES (values);
        db.session.add(new_user)
        # add the user to the DB and commit changes
        db.session.commit()
        login_user(new_user)
        # if registered and login successfully the user redirected to the personal page
        return redirect(url_for("personal"))
    # if it's GET method, register page opened with the form
    return render_template("register.html", form=form)


@app.route("/personal", methods=["GET", "POST"])
def personal():
    if current_user.is_authenticated:
        return render_template("personal.html")
    # if there is no authenticated user, redirect to the home page
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    username = request.args.get("username")
    if username:  # check if username was send in the link and add it to the form
        form.username.data = username
    if form.validate_on_submit():
        # when validated, search user in the DB, and check the password
        username = form.username.data
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            flash("This account does not exist.", "error")
            return redirect(url_for("login"))
        if not check_password_hash(user.password, form.password.data):
            flash("The password is wrong.", "error")
            return redirect(url_for("login"))
        # if everything is ok, log in the user, and redirect to the home page
        login_user(user)
        return redirect(url_for("home"))
    # if it's GET, show login page with the form
    return render_template("login.html", form=form)


@app.route("/logout")  # this is obviously a logout function
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Post()
        new_post.title = form.title.data
        new_post.content = form.content.data
        new_post.date = date_time()
        new_post.author = current_user
        db.session.add(new_post)
        # here is another INSERT and commit
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):  # post_id comes from the url as int
    form = CommentForm()
    requested_post = db.get_or_404(Post, post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Login or register to comment.")
            return redirect(url_for("login"))
        text = clean_html(form.text.data)
        new_comment = Comment()
        new_comment.content = text
        new_comment.date = date_time()
        new_comment.author = current_user
        new_comment.post = requested_post
        # here we add a comment, that belongs to author (user) and post.
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=requested_post.id))
    return render_template("post.html", post=requested_post, form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    post = db.get_or_404(Post, post_id)
    if current_user.id != post.author_id and current_user.id != 1:
        return redirect(url_for("show_post", post_id=post.id))
    edit_form = CreatePostForm(title=post.title, content=post.content)
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.content = clean_html(edit_form.content.data)
        # UPDATE Post SET columns=values WHERE Post.ID=post_id;
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template(
        "make-post.html", form=edit_form, is_edit=True, title=post.title
    )


@app.route("/user")  # view user info
def view_user():
    uid = request.args.get("uid")  # get uid from html args
    if uid and uid.isdecimal():
        user = db.get_or_404(User, int(uid))
        return render_template("user-page.html", user=user)
    return redirect(url_for("home"))


@app.route("/admin")
def admin():
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    visitors = None  # get_visitors()
    users = db.session.query(User).order_by(User.id).all()
    return render_template("admin.html", all_users=users, visitors=visitors)


@app.route("/personal/edit", methods=["GET", "POST"])
def edit_personal():  # edit personal data
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    form = PersonalForm()
    if request.method != "POST":
        form.username.data = current_user.username
        form.name.data = current_user.name
        form.lastname.data = current_user.lastname
    if form.validate_on_submit():
        username = form.username.data
        current_user.name = form.name.data
        current_user.lastname = form.lastname.data
        if username != current_user.username:
            # if username changed, check whether it exists in the DB
            if db.session.query(User).filter_by(username=username).first():
                flash("This username is already registered.", "error")
                return redirect(url_for("edit_personal"))
            current_user.username = username
        # if everything is ok, perform UPDATE and commit
        db.session.commit()
        return redirect(url_for("personal"))
    return render_template("edit-personal.html", form=form)


@app.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):  # edit user data for administrator
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    user = db.get_or_404(User, user_id)
    form = PersonalForm(username=user.username, name=user.name, lastname=user.lastname)
    if form.validate_on_submit():
        user.username = form.username.data
        user.name = form.name.data
        user.lastname = form.lastname.data
        db.session.commit()
        return redirect(url_for("edit_user", user_id=user.id))
    return render_template("edit-user.html", form=form, user=user)


### DELETE functions ###
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    post_to_delete = db.get_or_404(Post, post_id)
    if current_user.id == post_to_delete.author_id or current_user.id == 1:
        db.session.delete(post_to_delete)
        # DELETE FROM Post WHERE Post.ID=post_id; and commit
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete/post/<int:post_id>/comment/<int:comment_id>")
def delete_comment(post_id, comment_id):
    if not current_user.is_authenticated:
        return redirect(url_for("home"))
    comment_to_delete = db.get_or_404(Comment, comment_id)
    if current_user.id == comment_to_delete.author_id or current_user.id == 1:
        db.session.delete(comment_to_delete)
        db.session.commit()
    return redirect(url_for("show_post", post_id=post_id))


@app.route("/admin/user/<int:user_id>/delete")
def delete_user(user_id):
    if not current_user.is_authenticated or current_user.id != 1:
        return redirect(url_for("home"))
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
