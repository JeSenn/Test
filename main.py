import pandas as pd
import datetime

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from forms import RegistrationForm, LoginForm, PostForm
from flask_wtf import Form
from wtforms import StringField, PasswordField
from flask_wtf.file import FileField
from wtforms.validators import InputRequired, Email, Length, AnyOf
from flask_bootstrap import Bootstrap


###############################################################################
# Config
###############################################################################

app = Flask(__name__)
Bootstrap(app)

app.config["SECRET_KEY"] = "not-telling"

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

###############################################################################
# Databases
###############################################################################

class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key = True)
     first_name = db.Column(db.String(20), nullable = False)
     last_name = db.Column(db.String(20), nullable = False)
     user_handle = db.Column(db.String(20), unique = True, nullable = False)
     email = db.Column(db.String(30), unique = True, nullable = False)
     password = db.Column(db.String(30), nullable = False)
     description = db.Column(db.String(200))

     def __repr__(self):
         return f"User(id: '{self.id}', first_name: '{self.first_name}', " +\
               f" last_name: '{self.last_name}', email: '{self.email}' " +\
               f" user_handle: '{ self.user_handle}') "

class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(140), nullable = False)
    user_handle = db.Column(db.String(20), nullable=False)
    length = db.Column(db.Integer, nullable=True)
    time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f"User(id: '{self.id}', name: '{self.name}', " +\
                   f" email: '{self.email}')"

###############################################################################
# App Routes
###############################################################################

@app.route("/")
def index():
    post = Posts.query.order_by(Posts.time.desc())
    return render_template("homepage.html", post=post)

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistrationForm()

    if form.validate_on_submit():
        registration_worked = register_user(form)
        if registration_worked:
            return redirect(url_for("login"))

    return render_template("registration.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        if is_login_successful(form):
            return redirect(url_for("index"))
        else:
            flash("Login Unsuccessful")
            return redirect(url_for("registration"))
    return render_template("login.html", form=form)

@app.route("/posts", methods=["GET", "POST"])
@login_required
def posts():
    form = PostForm()

    if form.validate_on_submit():

        add_post(form)
        return redirect(url_for("index"))


    return render_template("posts.html", form=form)

@app.route("/profile/<user_handle>")
@login_required
def profile(user_handle):
    logged_in = User.query.filter_by(user_handle = user_handle).first()
    post = Posts.query.filter_by(user_handle = user_handle).order_by(Posts.time.desc())
    return render_template("profile.html", logged_in=logged_in, post=post)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


###############################################################################
# Helper functions
###############################################################################
def register_user(form_data):

    def email_already_taken(email):
        if User.query.filter_by(email=email).count() > 0:
            return True
        else:
            return False

    if email_already_taken(form_data.email.data):
        flash("this Email is already taken!")
        return False

    hashed_password = bcrypt.generate_password_hash(form_data.password.data)

    user = User(first_name=form_data.first_name.data,
                last_name=form_data.last_name.data,
                user_handle=form_data.user_handle.data,
                description=form_data.description.data,
                email=form_data.email.data,
                password=hashed_password)

    db.session.add(user)

    db.session.commit()

    return True

def is_login_successful(form_data):

    email = form_data.email.data
    password = form_data.password.data

    user = User.query.filter_by(email=email).first()

    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            login_user(user)

            return True

    return False

def add_post(form_data):
    length = len(form_data.content.data)


    post = Posts(content=form_data.content.data,
                       user_id=current_user.id,
                       user_handle=current_user.user_handle,
                       length=length)

    db.session.add(post)

    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
