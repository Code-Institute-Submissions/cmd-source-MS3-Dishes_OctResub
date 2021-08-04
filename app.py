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
    course = mongo.db.dish.find()
    return render_template("home.html", dishes=course)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing = mongo.db.users.find_one(
            {"user_name": request.form.get("user_name").lower})

        if existing:
            flash("Username not available")
            redirect(url_for("register"))

        new_user = {
            "first_name": request.form.get("first_name").lower(),
            "last_name":  request.form.get("last_name").lower(),
            "user_name":  request.form.get("user_name").lower(),
            "user_password":  request.form.get("user_password").lower(),
            "user_email":  request.form.get("user_email").lower(),
        }
        mongo.db.users.insert_one(new_user)

        session["user_cookie"] = request.form.get("user_name").lower()


    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)