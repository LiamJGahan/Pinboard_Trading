from helpers import apology, lookup, lookup_overview
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from dotenv import load_dotenv
import os

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database config (Clever Cloud)
def create_connection():
    connection = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )
    return connection 

# Citation - Harvardx CS50x Finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
       
        # Query database for username
        cur = create_connection()
        if cur:
            cursor = cur.cursor()
            username = request.form.get("username")
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            rows = cursor.fetchall()
            cursor.close()
            cur.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0][2], request.form.get("password") 
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Citation - Harvardx CS50x Finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# index
@app.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")
    connection = create_connection()
    card_list = []

    if request.method == "POST":
        symbol = request.form["symbol"].upper()

        if not symbol:
            return apology("Must enter symbol", 400)

        price = lookup(symbol)
        overview = lookup_overview(symbol)

        if price and overview:
            card = {**price, **overview}

            cursor = connection.cursor()

            # Check if stock exists, if not, add a new one
            cursor.execute("SELECT * FROM stocks WHERE user_id = %s AND symbol = %s", (user_id, symbol))
            stock = cursor.fetchone()

            if not stock:
                cursor.execute("""INSERT INTO stocks (user_id, symbol, name, price, industry, description, market_cap)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user_id, card["symbol"], card["name"], card["price"], card["industry"], card["description"], card["market_cap"]))
                connection.commit()

            cursor.close()
        else:
            return apology("Alphavantage API limit reached", 503)

    # Get stocks
    cursor2 = connection.cursor()
    cursor2.execute("SELECT symbol, name, price FROM stocks WHERE user_id = %s", (user_id,))
    rows = cursor2.fetchall()

    for row in rows:
        card_list.append({
            "symbol": row[0],
            "name": row[1],
            "price": row[2],
        })

    cursor2.close()
    connection.close()

    return render_template("index.html", card_list=card_list)

# Remove for deployment
if __name__ == '__main__':
    app.run(port=5002)