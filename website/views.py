from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import User, Story, Contribution, Like
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("base.html", user=current_user)
