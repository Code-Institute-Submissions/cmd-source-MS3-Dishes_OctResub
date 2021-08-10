import os
from flask import (
    Flask, flash, render_template,redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)
# The authentication config vars were taken from the PythonMiniProject
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/dishes")
def dishes():
    course = mongo.db.dish.find()
    return render_template("dishes.html", dishes=course)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing = mongo.db.dish_users.find_one(
            {"user_name": request.form.get("user_name").lower()})

        if existing:
            flash("Username not available")
            return redirect(url_for("register"))

        new_user = {
            "first_name": request.form.get("first_name").lower(),
            "last_name":  request.form.get("last_name").lower(),
            "user_name":  request.form.get("user_name").lower(),
            "user_password": generate_password_hash(request.form.get(
                "user_password").lower()),
            "user_email":  request.form.get("user_email").lower(),
        }
        mongo.db.dish_users.insert_one(new_user)

        session['user_cookie'] = request.form.get("user_name").lower()
    return render_template("register.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("user_name")
        password = request.form.get("user_password")
        user = mongo.db.dish_users.find_one({"user_name": username})
        if user and check_password_hash(user["user_password"], password):
            flash("Welcome, {}".format(request.form.get("user_name")))
            session['user_cookie'] = request.form.get("user_name").lower()
            return redirect(url_for("profile", username=session['user_cookie']))
        else:
            flash("incorrect password/username")
    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.dish_users.find_one(
        {"user_name": session['user_cookie']})["user_name"]

    first = mongo.db.dish_users.find_one(
        {"user_name": session['user_cookie']})["first_name"]

    last = mongo.db.dish_users.find_one(
        {"user_name": session['user_cookie']})["last_name"]

    email = mongo.db.dish_users.find_one(
        {"user_name": session['user_cookie']})["user_email"]
    
    if session['user_cookie']:
        return render_template(
            "profile.html", username=username, first=first, last=last, email=email)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user_cookie")
    return redirect(url_for("login"))

@app.route("/utensils")
def utensils():
    return render_template("utensils.html")


@app.route("/newdish", methods=["GET", "POST"])
def newdish():
    new_dish = mongo.db.dish_type.find().sort("dish_type_name", 1)
    return render_template("newdish.html", dishes=new_dish)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)