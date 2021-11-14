from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, Flask, render_template, request, jsonify, redirect, url_for, request, flash
from flask_login import login_required, current_user
from newsapi import NewsApiClient
from pusher import Pusher
from .models import User,History
from . import db
import uuid
import json
import requests
import os

main = Blueprint('main', __name__)

pusher = Pusher(
      app_id = os.environ.get("PUSHER_ID"),
      key = os.environ.get("PUSHER_KEY"),
      secret = os.environ.get("PUSHER_SECRET"),
      cluster = os.environ.get("PUSHER_CLUSTER"),  
      ssl = os.environ.get("PUSHER_SSL")
    )

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    newsapi_client = NewsApiClient(api_key = os.environ.get("NEWSAPI_APIKEY"))
    top_headlines = newsapi_client.get_top_headlines(q = os.environ.get("NEWS_Q"), category = os.environ.get("NEWS_CAT"))
    newsData = []
    for article in top_headlines["articles"]:
        newsData.append({"title" : article["title"],
                         "url": article["url"],
                         "urlToImage" : article["urlToImage"],
                         "description": article["description"],
                         "author": article["author"]})
    return render_template('profile.html', name = current_user.name, feed = newsData[:4])

 
@main.route('/news')
@login_required
def news():
    newsapi_client = NewsApiClient(api_key = os.environ.get("NEWSAPI_APIKEY"))
    top_headlines = newsapi_client.get_top_headlines(q = os.environ.get("NEWS_Q"),category = os.environ.get("NEWS_CAT"))
    newsData = []
    for article in top_headlines["articles"]:
        newsData.append({"title" : article["title"], "url": article["url"], "urlToImage" : article["urlToImage"]})
    return render_template('news.html', name = current_user.name, feed = newsData[:20])

@main.route('/community')
@login_required
def community():
    return render_template('community.html')

@main.route('/team')
@login_required
def team():
    return render_template('team.html')

@main.route('/blog')
@login_required
def blog():
    return render_template('blog.html')

@main.route('/personal')
@login_required
def personal():
    email = current_user.email
    history = User.query.filter_by(email = email).first().post
    return render_template('personal.html', history = history)

@main.route('/planner')
@login_required
def planner():
    mealplan = current_user.mealplan
    return render_template('diet.html', mealplan=json.loads(mealplan))

@main.route('/about')
@login_required
def about():
    email = current_user.email
    user = User.query.filter_by(email = email).first()
    return render_template('about.html', user = user)

@main.route("/updateprof")
@login_required
def updateProfile():
    email = current_user.email
    user = User.query.filter_by(email = email).first()
    return render_template("update_profile.html", user_det = user)

@main.route("/updatedb", methods=["POST"])
@login_required
def updateDb():
    email = current_user.email
    password = request.form.get("password") if request.form.get("password") else current_user.password
    age = request.form.get("age") if request.form.get("age") else current_user.age
    height = request.form.get("height") if request.form.get("height") else current_user.height
    weight = request.form.get("weight") if request.form.get("weight") else current_user.weight
    bmi = current_user.bmi if current_user.bmi else round(float(weight)/(float(height)/100)**2)
    country = request.form.get("country") if request.form.get("country") else current_user.country
    dob = request.form.get("dob") if request.form.get("dob") else current_user.dob
    gender = request.form.get("gender") if request.form.get("gender") else current_user.gender
    calories = request.form.get("calories") if request.form.get("calories") else current_user.calories
    diet = request.form.get("diet") if request.form.get("diet") else current_user.diet
    if current_user.mealplan:
        mealplan = current_user.mealplan
    else:
        parameters = {
        "timeFrame": os.environ.get("FOOD_TIMEFRAME"),
        "targetCalories":calories,
        "diet":diet,
        "hash":os.environ.get("FOOD_API_HASH"),
        "apiKey":os.environ.get("FOOD_API_APIKEY")
        }
        response = requests.get("https://api.spoonacular.com/mealplanner/generate", params = parameters)
        data = json.loads(response.text)
        mealplan = json.dumps(data)

    update_user = User.query.filter_by(email=email).update(dict(
    password = password,
    age = age, 
    height = height,
    weight = weight,
    bmi = bmi,
    country = country,
    dob = dob,
    gender = gender,
    diet = diet,
    calories = calories,
    mealplan = mealplan))
    db.session.commit()
    return redirect(url_for("main.about"))
    
@main.route('/post', methods=['POST'])
@login_required
def addPost():
    data = {
    'id': "post-{}".format(uuid.uuid4().hex),
    'title': request.form.get('title'),
    'content': request.form.get('content'),
    'status': 'active',
    'event_name': 'created'
    }
    pusher.trigger("blog", "post-added", data)
    email = current_user.email
    user = User.query.filter_by(email=email).first()
    new_post = History(
        email = email,
        post_id = data["id"],
        title = data["title"],
        content = data["content"],
        status = data["status"],
        event_name = data["event_name"],
        posts = user
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(data)

@main.route('/post/<id>', methods=['PUT','DELETE'])
@login_required
def updatePost(id):
    data = { 'id': id }
    if request.method == 'DELETE':
        data['event_name'] = 'deleted'
        pusher.trigger("blog", "post-deleted", data)
    else:
        data['event_name'] = 'deactivated'
        pusher.trigger("blog", "post-deactivated", data)
    return jsonify(data)
