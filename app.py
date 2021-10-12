import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
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

'''
Custom 404 page which was inspired by
https://www.youtube.com/watch?v=3O4ZmH5aolg
'''


@app.errorhandler(404)
def error_404(e):
    return render_template('404.html'), 404


# Renders the homepage for Cookbook
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


# Renders the available dishes for Cookbook from MongoDB
@app.route("/dishes")
def dishes():
    course = mongo.db.dish.find()
    return render_template("dishes.html", dishes=course)


# Searches the available dishes in the DB
@app.route("/searchdishes", methods=["GET", "POST"])
def searchdishes():
    search = request.form.get("search")
    course = list(mongo.db.dish.find({"$text": {"$search": search}}))
    return render_template("dishes.html", dishes=course)


'''
Renders the registration page page and checks to see
if a user already exists before adding a new user
'''


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


'''
Renders the login page and checks to see
if the username and password are correct
'''


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("user_name")
        password = request.form.get("user_password")
        user = mongo.db.dish_users.find_one({"user_name": username})
        if user and check_password_hash(user["user_password"], password):
            flash("Welcome, {}".format(request.form.get("user_name")))
            session['user_cookie'] = request.form.get("user_name").lower()
            return redirect(url_for(
                "profile", username=session['user_cookie']))
        else:
            flash("incorrect password/username")
    return render_template("login.html")


# Renders the profile page for some basic info of the user


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):

    course = mongo.db.dish.find()

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
            "profile.html", username=username, first=first,
            last=last, email=email, dishes=course)
    return redirect(url_for("login"))


# Logs the user out by removing the session cookie


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user_cookie")
    return redirect(url_for("login"))

# Renders cooking utensils page where the owner sells their products


@app.route("/utensils")
def utensils():
    return render_template("utensils.html")

# Renders the page for adding dishes to the selection of recipes available


@app.route("/newdish", methods=["GET", "POST"])
def newdish():
    if request.method == "POST":
        add_dish = {
            "dish_name": request.form.get("dish"),
            "dish_type": request.form.get("dish_type_name"),
            "dish_description": request.form.get("description"),
            "created_by": session['user_cookie']
        }
        mongo.db.dish.insert_one(add_dish)
        flash("Your dish was added")
        return redirect(url_for("dishes"))
    new_dish = mongo.db.dish_type.find().sort("dish_type_name", 1)

    return render_template("newdish.html", dishes=new_dish)

# Renders the page for editing dishes


@app.route("/update_dish/<dish_id>", methods=["POST", "GET"])
def update_dish(dish_id):
    if request.method == "POST":
        update_dish = {
            "dish_name": request.form.get("dish"),
            "dish_type": request.form.get("dish_type_name"),
            "dish_description": request.form.get("description")
        }
        new_dish = mongo.db.dish.update({"_id": ObjectId(dish_id)}, update_dish)
        flash("Your dish was updated")

    dish = mongo.db.dish.find_one({"_id": ObjectId(dish_id)})
    new_dish = list(mongo.db.dish_type.find().sort("dish_type_name", 1))

    return render_template("update_dish.html", dish=dish, dishes=new_dish)

# Deletes a selected recipe and returns the user to the dishes page


@app.route("/delete_dish/<dish_id>", methods=["POST", "GET"])
def delete_dish(dish_id):
    mongo.db.dish.remove({"_id": ObjectId(dish_id)})
    flash("The selected dish was deleted")
    return redirect(url_for('dishes'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
