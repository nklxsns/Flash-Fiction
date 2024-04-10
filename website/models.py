from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(50), unique=True)
    bio = db.Column(db.String(250))
    password = db.Column(db.String(150))

    stories = db.relationship("Story", backref="user", passive_deletes=True)
    contributions = db.relationship("Contribution", backref="user", passive_deletes=True)
    likes_story = db.relationship("Like_story", backref="user", passive_deletes=True)
    likes_contribution = db.relationship("Like_contribution", backref="user", passive_deletes=True)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    part1 = db.Column(db.String(500))
    part2 = db.Column(db.String(500))
    part3 = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    contributions = db.relationship("Contribution", backref="story", passive_deletes=True)
    likes = db.relationship("Like_story", backref="story", passive_deletes=True)

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    content = db.Column(db.String(1500))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id", ondelete="CASCADE"), nullable=False)

    likes = db.relationship("Like_contribution", backref="contribution", passive_deletes=True)

class Like_contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    contribution_id = db.Column(db.Integer, db.ForeignKey("contribution.id", ondelete="CASCADE"), nullable=False)

class Like_story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id", ondelete="CASCADE"), nullable=False)
