import os

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["SECRET_KEY"] = "Youcan'tguess!"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://pupaesdzdmnugi:568dbf9fb18b5be76c7b624ae77ee6d365c74375ceef01c35ef49379973a5102@ec2-35-169-254-43.compute-1.amazonaws.com:5432/d78uju11s198k4"


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for("login"))
    return wrap

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    users = db.execute("SELECT * FROM users").fetchall()
    username = request.form.get("inputUsername")
    hashed_password=bcrypt.generate_password_hash(request.form.get("inputPassword"))
    user_id=db.execute("SELECT * FROM users WHERE users_id=users.id")

    #import mysql.connector
    #from datetime import datetime
    #cursor = connection.cursor()
    #now = datetime.now()
    #id = 1
    #login_date = now.strftime('%Y-%m-%d %H:%M:%S')


    error = None
    if request.method == "POST":
        if (request.form["username"] != "users.username") \
                or request.form["password"] != "users.hashed_password":
            return render_template("error.html", message="Invalid Username or Password.")
        else:
            session["logged_in"] = True
            flash("You are logged in.")
            return redirect(url_for("dashboard"))
    #cursor.execute("INSERT INTO logindata (id, login_date) VALUES(%s, %s)", {id, login_date})
    #db.session.commit()
    return render_template("login.html", error=error, users=users)
    

    
@app.route("/register", methods=["GET", "POST"])
def register():

    users = db.execute("SELECT * FROM users").fetchall()

    # Get registration information.
    username = request.form.get("inputUsername")
    email = request.form.get("inputEmail")
    hashed_password=bcrypt.generate_password_hash(request.form.get("inputPassword"))

    try:
        users.username = (request.form.get("inputUsername"))
    except ValueError:
        return render_template("error.html", message="Username not available. Try another username.")
    
    # Add user into the users table
    db.execute("INSERT INTO users (username, email, hashed_password) VALUES(:username, :email, :hashed_password)",
            {"username": username, "email": email, "hashed_password": hashed_password})
    db.session.commit()
    
    flash("Your account has been successfully created. You can log in now.")
    return redirect(url_for("login")) 
    return render_template("register.html", users=users)

@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    flash("You were logged out.")
    return redirect(url_for("index"))    

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/book", methods=["POST", "GET"])
@login_required
def book():
    """Review a Book"""
    
    user_id = db.execute("SELECT * FROM users WHERE id=users_id").fetchall()
    name = request.form.get("name")
    books = db.execute("SELECT * FROM books").fetchall()
    try:
        book_id = int(request.form.get("book_id"))
    except ValueError:
        return render_template("error.html", message="Invalid book number.")

    # Make sure the book exists.
    if db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).rowcount == 0:
        return render_template("error.html", message="No such book with that id.")
    db.execute("INSERT INTO reviews (user_id, book_id) VALUES (:user_id, :book_id)",
            {"user_id": user_id, "book_id": book_id})
    db.commit()
    return render_template("books.html", books=books)

if __name__ == "__main__":
    app.run(debug=True)