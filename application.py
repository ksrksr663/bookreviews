import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/registration", methods=["POST"])
def registration():
    # grab user's info from the form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    hashed_password = generate_password_hash(password)  # hash the password

    # insert user's info into the database
    db.execute("INSERT INTO users (first_name, last_name, username, password) VALUES (:first_name, :last_name, :username, :password)", {"first_name": first_name, "last_name": last_name, "username": username, "password": hashed_password})
    db.commit()  # finalize the transaction

    return render_template("success.html", foo="registered", username=username)

@app.route("/login")
def login():
    return render_template("log_in.html")


@app.route("/login_process", methods=["POST"])
def login_process():
    # grab info from the form
    username = request.form.get("username")
    password = request.form.get("password")

    # grab the corresponding username from the database
    username_from_database = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if username_from_database is None:  # if no username was matched in the database
        return render_template("error.html", nonexistent_username=True)

    # got the username, but does he/she have the right password?
    password_from_database = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    # password_from_database = db.execute("SELECT password FROM users WHERE username = :username", {"username": username}) --> doesn't work!!!
    # password_from_database = db.execute("SELECT password FROM users WHERE username = :username", {"username": username}).fetchone() --> doesn't work as well!!!
    password_from_database = password_from_database.password  # just get the password, not the entire row
    # do the hashes match?
    if not check_password_hash(password_from_database, password):  # returns False if they don't match
        return render_template("error.html", wrong_password=True)

    # looks like the user has the right username and password, so let the user be logged in
    return render_template("success.html", foo="logged", username=username)



if __name__ == "__main__":
    app.run()

