import os
import pandas as pd
import numpy as np
import sqlite3

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db_users = SQL("sqlite:///anime.db")
db_info = SQL("sqlite:///list.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/home")
def home():
    # Homepage providing an overview of the website
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Log user in

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password.", 403)

        # Query database for username
        rows = db_users.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid username and/or password.", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # Render login page
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Log user out
    session.clear()

    return redirect("/home")


@app.route("/")
def index():
    # If a user is currently logged in
    if "user_id" in session:
        return render_template("index.html")
    # If a user is visiting the website only
    else:
        return redirect("/home")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Register user
    if request.method == "POST":

        # If the user trying to register DID NOT PROVIDE a USERNAME.
        if not request.form.get("username"):
            return apology("Please provide a username.", 400)

        # If the user trying to register DID NOT PROVIDE a PASSWORD.
        elif not request.form.get("password"):
            return apology("Please provide a password.", 400)

        # If the user trying to register DID NOT CONFIRM their PASSWORD.
        elif not request.form.get("confirmation"):
            return apology("Please confirm password.", 400)

        # If the user trying to register SUBMITTED PASSWORDS that DO NOT MATCH.
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.", 400)

        # Check database for matching records of USERNAME.
        rows = db_users.execute("SELECT * FROM users WHERE username = ?",
                                request.form.get("username"))

        # If a MATCH is FOUND, return a message informing user of the circumstance.
        if len(rows) != 0:
            return apology("Username already exists.", 400)

        # Insert the valid username and password of the user who finished registration
        db_users.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                         request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Executes a SQL query to retrieve all colums that matches the username provided by the user.
        rows = db_users.execute("SELECT * FROM users WHERE username = ?",
                                request.form.get("username"))

        # Sets the user_id in the session to log the user in immediately after registration.
        session["user_id"] = rows[0]["id"]

        # Redirects user to the home page after successful registration.
        return redirect("/")

    # Render the registration page.
    else:
        return render_template("register.html")


@app.route("/random_anime")
def random_anime():
    # Correctly construct the file path
    file_path = os.path.join('static', 'trending_anime.csv')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return "File not found", 404

    # Load the dataset
    df = pd.read_csv(file_path)

    # Print column names and the first few rows to verify
    print("Columns:", df.columns)
    print("First few rows of the dataset:")
    print(df.head())

    # Replace NaN values with default values
    df['English'].fillna('Unknown Title', inplace=True)
    df['Description'].fillna('No description available', inplace=True)

    # Shuffle the DataFrame to randomize the order
    df_shuffled = df.sample(frac=1, random_state=np.random.randint(0, 10000)
                            )  # Use random_state for reproducibility

    # Select a subset of animes (e.g., 5 random animes)
    df_random = df_shuffled.head(6)

    # Print the random DataFrame to verify
    print("Random DataFrame:")
    print(df_random)

    # Select relevant columns and rename them for clarity
    random_anime_list = df_random[['English', 'Popularity', 'Rank', 'Description']].rename(columns={
        'English': 'Title'
    }).to_dict(orient='records')

    # Print the random list to verify
    print("Random Anime List:", random_anime_list)

    return render_template('random_anime.html', anime_list=random_anime_list)


@app.route("/list", methods=["GET", "POST"])
def list():
    if request.method == "POST":
        # Add the user's entry into the database
        title = request.form.get("title")
        rank = request.form.get("rank")
        if not title or not rank:
            return redirect("/list")

        # Insert user input into the database with the default status 'Pending'
        db_info.execute("INSERT INTO list (title, rank, status) VALUES(?, ?, ?)",
                        title, rank, "Pending")

        # Redirect to the list page after adding an entry.
        return redirect("/list")

    else:
        # Display the entries in the database on list.html
        entries = db_info.execute("SELECT * FROM list")
        return render_template("list.html", entries=entries)


@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    # Update the status of the anime to 'Finished'
    db_info.execute("UPDATE list SET status = 'Finished' WHERE id = ?", id)
    return redirect("/ratings")


@app.route("/ratings")
def ratings():
    # Connect to your database
    conn = sqlite3.connect('list.db')
    cursor = conn.cursor()

    # Execute the query
    cursor.execute("""
        SELECT l.id, l.title, l.rank, r.rating, r.comment, r.submitted
        FROM list l
        LEFT JOIN ratings r ON l.id = r.anime_id
        WHERE l.status = 'Finished'
    """)

    # Fetch all rows
    animes = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with the fetched data
    return render_template("ratings.html", animes=animes)


@app.route("/submit_rating/<int:anime_id>", methods=["POST"])
def submit_rating(anime_id):
    # Get rating and comment from form data
    rating = request.form.get(f'rating_{anime_id}')
    comment = request.form.get(f'comment_{anime_id}')
    print(f"Rating: {rating}, Comment: {comment}")

    # Debug prints to check received values
    print(f"Received rating: '{rating}', comment: '{comment}' for anime_id: {anime_id}")

    # Connect to the database
    conn = sqlite3.connect('list.db')
    cursor = conn.cursor()

    # Check if there's already an entry for this anime_id in the ratings table
    existing_rating = cursor.execute(
        "SELECT * FROM ratings WHERE anime_id = ?", (anime_id,)).fetchone()

    if existing_rating:
        # Update existing rating
        cursor.execute("""
            UPDATE ratings
            SET rating = ?, comment = ?, submitted = 1
            WHERE anime_id = ?
        """, (rating, comment, anime_id))
    else:
        # Insert new rating
        cursor.execute("""
            INSERT INTO ratings (anime_id, rating, comment, submitted)
            VALUES (?, ?, ?, 1)
        """, (anime_id, rating, comment))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    # Redirect back to the ratings page
    return redirect("/ratings")
