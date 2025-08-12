from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret_key"

UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    if not os.path.exists("travel.db"):
        conn = sqlite3.connect("travel.db")
        c = conn.cursor()

        c.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')

        c.execute('''CREATE TABLE trips (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        location TEXT,
                        image TEXT,
                        cost REAL,
                        heritage TEXT,
                        places TEXT,
                        created_at TEXT
                    )''')

        conn.commit()
        conn.close()

@app.route("/")
def index():
    conn = sqlite3.connect("travel.db")
    c = conn.cursor()
    c.execute("SELECT trips.id, trips.location, trips.image, trips.cost, trips.heritage, trips.places, users.username FROM trips JOIN users ON trips.user_id = users.id ORDER BY trips.id DESC")
    trips = c.fetchall()
    conn.close()
    return render_template("index.html", trips=trips)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("travel.db")
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except:
            conn.close()
            return "Пользователь уже существует!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("travel.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("index"))
        else:
            return "Неверный логин или пароль!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/add_trip", methods=["GET", "POST"])
def add_trip():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        location = request.form["location"]
        cost = request.form["cost"]
        heritage = request.form["heritage"]
        places = request.form["places"]

        image_file = request.files["image"]
        filename = None
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)

        conn = sqlite3.connect("travel.db")
        c = conn.cursor()
        c.execute("INSERT INTO trips (user_id, location, image, cost, heritage, places, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (session["user_id"], location, filename, cost, heritage, places, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("add_trip.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
