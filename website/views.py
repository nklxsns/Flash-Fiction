from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.sql import func
import os
from .models import User, Story, Contribution, Like_story, Like_contribution
from . import db


UPLOAD_FOLDER = 'website/static/images/profile-imgs' 

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    stories = db.session.query(Story).outerjoin(Like_story).group_by(Story.id).order_by(func.count(Like_story.id).desc()).all()

    return render_template("homepage.html", user=current_user, stories=stories)


@views.route("/view-story/<int:id>")
@login_required
def view_story(id:int):
    story = Story.query.filter_by(id=id).first()
    contributions = db.session.query(Contribution).filter_by(story_id=id).outerjoin(Like_contribution).group_by(Contribution.id).order_by(func.count(Like_contribution.id).desc()).all()


    if not story:
        return redirect(url_for("views.home"))

    return render_template("story-view.html", story=story, user=current_user, contributions=contributions)

@views.route("/profile/<int:id>")
@login_required
def profile(id:int):
    user = User.query.filter_by(id=id).first()
    stories = db.session.query(Story).filter_by(user_id=id).outerjoin(Like_story).group_by(Story.id).order_by(func.count(Like_story.id).desc()).all()
    contributions = db.session.query(Contribution).filter_by(user_id=id).outerjoin(Like_contribution).group_by(Contribution.id).order_by(func.count(Like_contribution.id).desc()).all()

    return render_template("profile.html", user=current_user, profile_user=user, stories=stories, contributions=contributions)

@views.route("/edit-profile/<int:id>", methods=['GET', 'POST'])
@login_required
def edit_profile(id:int):
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
        new_profile_pic = request.files['imageUpload']

        if new_profile_pic.filename != "":
            _ , extention = new_profile_pic.filename.split('.')
            new_profile_pic.filename = str(current_user.id) + "." + extention
            user.profile_img = new_profile_pic.filename
            new_profile_pic.save(os.path.join(UPLOAD_FOLDER , new_profile_pic.filename))


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

@views.route("/delete-story/<int:id>")
@login_required
def delete_story(id:int):
    story = Story.query.filter_by(id=id).first()
    contributions = Contribution.query.filter_by(story_id=id).all()
    likes = Like_story.query.filter_by(story_id=id).all()
    if story and story.user.id == current_user.id:
        db.session.delete(story)
        for contribution in contributions:
            delete_contribution(contribution.id)

        for like in likes:
            db.session.delete(like)
        db.session.commit()

    else:
        return jsonify({"message": "You do not have the access."}, 400)
    
    return jsonify({"message": "Deleted successfully."}, 200)

@login_required
@views.route("/create-contribution/<int:story_id>", methods=['GET', 'POST'])
def create_contri(story_id:int):
    if request.method == "POST":
        data = request.json
    
        title = data.get("title")
        content = data.get("content")
        
        new_contribution = Contribution(title=title, content=content, user_id=current_user.id, story_id=story_id)

        db.session.add(new_contribution)
        db.session.commit()
        return redirect("/view-story/" + story_id)

    story = Story.query.filter_by(id=story_id).first()
    return render_template("contribution-create.html", story=story)

@views.route("/delete-contribution/<int:id>")
@login_required
def delete_contribution(id:int):
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

@views.route("/like-story/<int:story_id>")
@login_required
def like_story(story_id:int):
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

@views.route("/like-contribution/<int:contribution_id>")
@login_required
def like_contribution(contribution_id:int):
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
