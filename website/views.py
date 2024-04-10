from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import desc
import json
from .models import User, Story, Contribution, Like_story, Like_contribution
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    stories = Story.query.all()
    return render_template("homepage.html", user=current_user, stories=stories)


@views.route("/view-story/<id>")
@login_required
def view_story(id):
    story = Story.query.filter_by(id=id).first()
    contributions = Contribution.query.filter_by(story_id=id).all()

    if not story:
        return redirect(url_for("views.home"))

    return render_template("story-view.html", story=story, user=current_user, contributions=contributions)

@views.route("/profile/<id>")
@login_required
def profile(id):
    user = User.query.filter_by(id=id).first()

    return render_template("profile.html", user=current_user, profile_user=user, stories=user.stories, contributions=user.contributions)

@views.route("/edit-profile/<id>", methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    if request.method == 'POST':
        new_username = request.form['username']
        new_bio = request.form['bio']

        if new_username != current_user.username:
            check_username = User.query.filter_by(username=new_username).first()
            if check_username:
                flash("Username already taken.", category="error")
                return render_template("edit-profile.html", user=current_user)

        user = User.query.filter_by(id=id).first()
        user.username = new_username
        user.bio = new_bio
        db.session.commit()

        return redirect(url_for("views.profile", id=id))
    return render_template("edit-profile.html", user=current_user)

@views.route("/create-story", methods=['GET', 'POST'])
@login_required
def create_story():
    if request.method == "POST":
        data = request.json
    
        title = data.get("title")
        part1 = data.get("part1")
        part2 = data.get("part2")
        part3 = data.get("part3")

        new_story = Story(title=title, part1=part1, part2=part2, part3=part3, user_id=current_user.id)
        db.session.add(new_story)
        db.session.commit()
        return redirect("/home")
    return render_template("story-create.html")

@views.route("/delete-story/<id>")
@login_required
def delete_story(id):
    story = Story.query.filter_by(id=id).first()
    contributions = Contribution.query.filter_by(story_id=id).all()
    likes = Like_story.query.filter_by(story_id=id).all()
    if story and story.user.id == current_user.id:
        db.session.delete(story)
        for contribution in contributions:
            delete_contribution(contribution.story.id, contribution.id)

        for like in likes:
            db.session.delete(like)
        db.session.commit()

    else:
        return jsonify({"message": "You do not have the access."}, 400)
    
    return jsonify({"message": "Deleted successfully."}, 200)

@login_required
@views.route("/create-contribution/<story_id>", methods=['GET', 'POST'])
def create_contri(story_id):
    if request.method == "POST":
        data = request.json
    
        title = data.get("title")
        content = data.get("content")
        
        print(content)
        new_contribution = Contribution(title=title, content=content, user_id=current_user.id, story_id=story_id)

        db.session.add(new_contribution)
        db.session.commit()
        return redirect("/view-story/" + story_id)

    story = Story.query.filter_by(id=story_id).first()
    return render_template("contribution-create.html", story=story)

@views.route("/delete-contribution/<story_id>/<id>")
@login_required
def delete_contribution(story_id, id):
    contribution = Contribution.query.filter_by(id=id).first()
    likes = Like_contribution.query.filter_by(contribution_id=id).all()
    if contribution and contribution.user.id == current_user.id:
        db.session.delete(contribution)
        for like in likes:
            db.session.delete(like)
        db.session.commit()

    else:
        return jsonify({"message": "You do not have the access."}, 400)
    
    return jsonify({"message": "Deleted successfully."}, 200)

@views.route("/like-story/<story_id>")
@login_required
def like_story(story_id):
    story = Story.query.filter_by(id=story_id).first()
    like = Like_story.query.filter_by(user_id=current_user.id, story_id=story_id).first()

    if not story:
        return jsonify({"error": "Story does not exist."}, 400)

    elif like:
        db.session.delete(like)
        db.session.commit()

    else:
        new_like = Like_story(user_id=current_user.id, story_id=story_id)
        db.session.add(new_like)
        db.session.commit()

    return jsonify({"likes": len(story.likes), "liked": current_user.id in map(lambda x: x.user_id, story.likes)})

@views.route("/like-contribution/<contribution_id>")
@login_required
def like_contribution(contribution_id):
    contribution = Contribution.query.filter_by(id=contribution_id).first()
    like = Like_contribution.query.filter_by(user_id=current_user.id, contribution_id=contribution_id).first()

    if not contribution_id:
        return jsonify({"error": "Contribution does not exist."}, 400)

    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        new_like = Like_contribution(user_id=current_user.id, contribution_id=contribution_id)
        db.session.add(new_like)
        db.session.commit()

    return jsonify({"likes": len(contribution.likes), "liked": current_user.id in map(lambda x: x.user_id, contribution.likes)})
