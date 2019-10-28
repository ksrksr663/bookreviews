import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# import the below functions so that I can hash and authenticate passwords
from werkzeug.security import generate_password_hash, check_password_hash

# set up the 'DATABASE_URL' environment variable, so I don't have to manually set them up myself every single time!!!
import set_environ_var
set_environ_var.database_url()

# set up the Goodreads module
import goodreads

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
    # Start with the user currently logged out if the key never existed
    if session.get("is_logged_in") is None:
        session["is_logged_in"] = False
    return render_template("index.html")


@app.route("/register_page")
def register_page():
    return render_template("register.html")


@app.route("/registration", methods=["POST"])
def registration():
    # first have to check if the username does not already exists
    # if it does, then render the error page
    username = request.form.get("username")
    username_from_database = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
    if username_from_database is not None:  # then the username already exists!
        return render_template("error.html", username_exists=True)

    # grab user's info from the form
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    # username = request.form.get("username") <- duplicate line of code
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
    session["is_logged_in"] = True
    session["username"] = username  # set the username key to the value of the current username
    return render_template("success.html", foo="logged in", username=username)


def is_logged_in():
    """
    This function checks if the user is logged in. Return True if he/she is logged in.
    Else, return False.
    """
    # check if the user is logged in
    if session.get("is_logged_in") is False:  # the user is not logged in
        return False
    if session.get("is_logged_in") is None:  # the user is not logged in
        return False


@app.route("/search")
def search():
    # first check if the user is logged in
    if is_logged_in() is False:  # if not is_logged_in is not working! TODO: check why
        return render_template("error.html", not_logged_in=True)
    return render_template("search.html", username=session.get("username"))


@app.route("/log_out")
def log_out():
    """ log the user out and render the success page"""
    # session.get("is_logged_in") = False -> I think this won't work; TODO: need to clarify
    session["is_logged_in"] = False
    return render_template("success.html", foo="logged out", username=session.get("username"))


@app.route("/search_functionality", methods=["POST"])
def search_functionality():
    """this function does the search functionality, that is, tries to return matching results to whatever
       the user typed in.
    """
    book_name = request.form.get("book_name")  # get the data from the form
    book_name = book_name.title()  # normalize the data
    results = db.execute(f"SELECT * FROM books WHERE title LIKE '%{book_name}%'").fetchall()
    return render_template("search_results.html", results=results, count=len(results))


@app.route("/book_page/<string:isbn>", methods=["GET", "POST"])
def book_page(isbn):
    """
        This function makes individual pages for each book. This includes calling in the Goodreads API,
        and rendering the reviews made by other users.
    """
    if request.method == "POST":  # the user is trying to submit a review
        # grab info from the form
        review = request.form.get("review")
        rating = request.form.get("rating")
        username = session.get("username")  # grab the username that is currently logged in
        # insert the review info into the database
        db.execute("INSERT INTO reviews (username, isbn, reviews, rating) VALUES (:username, :isbn, :review, :rating)", {"username": username, "isbn": isbn, "review": review, "rating": rating})
        db.commit()  # close the transaction

    book_info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()  # grab the book's info from the database
    # if len(book_info) == 0:  to check if the book exists? Then render an error page
    goodreads_data = goodreads.main(isbn)  # grab the book's number of ratings & its avg rating from Goodreads and return it as a dict

    # grab other users' reviews, and don't include own user's review in the off chance that he/she already submitted a review for this particular book
    user_reviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND NOT username = :username", {"isbn": isbn, "username": session.get("username")}).fetchall()

    # if user already submitted a review, then don't render the form
    # if session.get("username") == user_reviews.username:  # this syntax is so wrong!
    username_from_database = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": session.get("username"), "isbn": isbn}).fetchone()
    # if username_from_database is not None:  # means he/she did submitted a review
    #     render_form = True
    # else:
    #     render_form = False
    #     own_rating = username_from_database.rating
    #     own_review = username_from_database.reviews

    return render_template("book_page.html", book=book_info, number_of_ratings=goodreads_data.get('number of ratings'), average_rating=goodreads_data.get('average rating'), user_reviews=user_reviews, own_stuff=username_from_database)


if __name__ == "__main__":
    app.run()

