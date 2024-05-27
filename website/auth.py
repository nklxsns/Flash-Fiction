from flask import Blueprint, request, render_template, redirect, url_for, flash
from . import db
from pathlib import Path
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Story, Contribution, Like_story, Like_contribution

from .views import delete_story, delete_contribution, UPLOAD_FOLDER

auth = Blueprint("auth", __name__)

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if username_exists:
            flash("Username already in use.", category='error')
        elif email_exists:
            flash("Email already in use. Please log in", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1), bio="Hey there! Welcome to my profile.", profile_img="default.jpg")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for("views.home"))

    return render_template("signup.html", user=current_user)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password.", category='error')
        else:
            flash("Username does not exist. Please sign up.", category='error')
    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/delete-user/<int:id>", methods=['POST'])
@login_required
def delete_user(id:int):

    if current_user.id != id:
        print(type(current_user.id), type(id))
        flash("You cannot delete this account.", category="error")
        return redirect(url_for("views.profile", id=id))

    password = request.form['password']
    if not check_password_hash(current_user.password, password):
        flash("Incorrect Password.", category='error')
        return redirect(url_for("views.profile", id=id))

    user = User.query.filter_by(id=id).first()
    stories = Story.query.filter_by(user_id=id).all()
    contributions = Contribution.query.filter_by(user_id=id).all()
    story_likes = Like_story.query.filter_by(user_id=id).all()
    contribution_likes = Like_contribution.query.filter_by(user_id=id).all()

    if not user:
        flash("User does not exist.", category='error')
        return redirect(url_for("views.profile", id=id))
    
    if user.profile_img != "default.jpg":
        os.remove(os.path.join(UPLOAD_FOLDER , user.profile_img))
        name, ext = user.profile_img.split(".")

        for file in Path(UPLOAD_FOLDER).glob(name + '.*') :
            file.unlink()

    for story in stories:
        delete_story(story.id)

    for contribution in contributions:
        delete_contribution(contribution.id)
    
    for story_like in story_likes:
        db.session.delete(story_like)
    
    for contribution_like in contribution_likes:
        db.session.delete(contribution_like)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("auth.logout"))