from flask_login import UserMixin
from . import db

class History(UserMixin, db.Model):
   
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key =  True)
    email = db.Column(db.String, db.ForeignKey("user.email"))
    post_id = db.Column(db.Integer)
    title = db.Column(db.String(50))
    content = db.Column(db.String(300))
    status = db.Column(db.String(10))
    event_name = db.Column(db.String(20))
    def __repr__(self):
        return '<History %r>' % self.id


class User(UserMixin, db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    country = db.Column(db.String(100))
    bmi = db.Column(db.Float)
    dob = db.Column(db.String(12))
    gender = db.Column(db.String(20))
    post = db.relationship('History', backref = db.backref('posts'))
    email = db.Column(db.String(100), unique = True)
    diet = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    mealplan = db.Column(db.String(20000))
    
    def __repr__(self):
        return '<User %r>' % self.email

