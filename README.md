# What-Anime-To-Watch
#### Video Demo:  https://youtu.be/TzYGtUZkRF4
#### Description: A website project for the CS50 course, built using HTML, CSS, JavaScript, Python, Flask, and Bootstrap. It features random anime title generation to suggest shows to users, with sections for tracking both pending and completed anime. The site also includes a page where users can rate and comment on the anime they have finished.

## Usage
To start the application, use the following commands (if using CS50 codespace):

```bash
cd project
flask run
```

## Functions Overview
#### `home` function in line 36
~~~python
@app.route("/home")
def home():
    # Homepage providing an overview of the website
    return render_template("home.html")
~~~
Within the app.py file, several functions were made to ensure the overall functionality of the website.

A few functions were copied from the previous CS50 Problem Sets as they were deemed usable in the inital plan for the website.

The first user-defined function was named 'home' in line 36 of the app.py file. This function only serves one purpose and that is to render the template of the home.html which provides the users an overview of the website.

#### `login` and `logout` function
~~~python
@app.route("/login", methods=["GET", "POST"])
def login():

@app.route("/logout")
def logout():
~~~
The second and third function within the app.py file is a login and logout function from the CS50 Problem entitled Finance. This functionality ensures that the users of the website should first register for an account before fully accessing the different sections of the website.

#### `index` function
~~~python
@app.route("/")
def index():
    # If a user is currently logged in
    if "user_id" in session:
        return render_template("index.html")
    # If a user is visiting the website only
    else:
        return redirect("/home")
~~~
In the second user-defined function named 'index' in line 88 of the app.py file, it enables the program to detect whether a user is logged in or is just browsing the website. It has a built-in code that ensures when a user is logged in, they can view the inside of the website which will land them on the index.html file. Instead, if they are not logged in, they will just view the cover page of the website and will redirect them to the home page or home.html.

#### `register` function
In the register function in line 98, we credit this functionality again to the CS50 Problem Set named Finance. This enables a user to register for an account to access the website and use its functions.

#### `random_anime` function
In the next function entitled 'random_anime' in line 146, I honestly asked for the help of ChatGPT to write this functionality since I do not have much of a background in handling .CSV files within a Python code that also deals with SQL. ChatGPT helped me realize the functionality I wanted and I did a few debugging using search engines because it was slightly faulty at first. This code uses the dataset from Kaggle and displays random anime titles, together with their rank and popularity among viewers, and displays six of them at once in the 'Suggestions' section of my website. When the website is refreshed, another batch of titles will be displayed.


#### `list` function
~~~python
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
~~~
In the 'list' function in line 189, I got my inspiration for this section in the Problem Set named 'birthdays' also from CS50. I have made major revisions and added a few functionalities to make it my own and provide the functionality I wanted for my website. The 'list' function enables users to add certain anime titles and their rank based on the 'Suggestions' section. There will also be two buttons on the right side named 'Pending' and 'Finished' respectively. By default, the 'Pending' button is highlighted since the anime has just been added to the list. On the other hand, if the user already finished the anime and clicks on the 'Finished' button. It will mark this anime as 'Finished' and redirects the user to the 'ratings' section which will enable the user to provide a specific rating and comment for this specific anime. Once a rating is submitted, it cannot be edited any longer.
