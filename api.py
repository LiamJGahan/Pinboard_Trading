from helpers import apology, lookup, lookup_overview, update_cards
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
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
        cursor_factory=RealDictCursor,
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
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 400)
       
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
            rows[0]["hash"], request.form.get("password") 
        ):
            return apology("Invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

@app.route("/password", methods=["GET", "POST"])
#@login_required  TODO
def password():
    """Change Password"""

    connection = create_connection()
    user_id = session.get("user_id")

    if user_id == None:
        connection.close()
        return apology("Must log in", 400)

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("oldpassword"):
            connection.close()
            return apology("must enter old password", 400)   

        cursor = connection.cursor()
        row = cursor.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        row = cursor.fetchone()
        cursor.close()

        # Ensure password is correct
        if not row or not check_password_hash(
            row["hash"], request.form.get("oldpassword")
        ):
            connection.close()
            return apology("user or old password is invalid", 400)

        # Ensure password was submitted
        elif not request.form.get("newpassword"):
            connection.close()
            return apology("must enter new password", 400)

        # Ensure re-entered password was submitted
        elif not request.form.get("confirmation"):
            connection.close()
            return apology("must re-enter new password", 400)

        # Ensure passwords match
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            connection.close()
            return apology("new passwords do not match", 400)

        # Add new user to database
        cursor2 = connection.cursor()
        hash = generate_password_hash(request.form.get("newpassword"))
        cursor2.execute("UPDATE users SET hash = %s WHERE id = %s", (hash, user_id))
        connection.commit()
        cursor2.close

        connection.close()
        return redirect("/")

    else:
        connection.close()
        return render_template("account.html")

# index
@app.route("/", methods=["GET", "POST"])
def index():
    """Create and display stock cards"""

    user_id = session.get("user_id")
    connection = create_connection()
    card_list = []

    if request.method == "POST":

        if user_id == None:
            connection.close()
            return apology("Must log in", 400)

        symbol = request.form["symbol"].upper()

        if not symbol:
            connection.close()
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
            connection.close()
            return apology("Alphavantage API limit reached", 503)        

    # Get stocks
    cursor2 = connection.cursor()
    cursor2.execute("SELECT symbol, name, price, timestamp FROM stocks WHERE user_id = %s", (user_id,))
    rows = cursor2.fetchall()
    cursor2.close()

    # Update the index cards if new day
    update_cards(rows, connection)

    for row in rows:
        card_list.append({
            "symbol": row["symbol"],
            "name": row["name"],
            "price": row["price"],
        })

    connection.close()

    return render_template("index.html", card_list=card_list)   

@app.route("/trade")
def trade():
    """Buy or sell stock"""

    # TODO

    return render_template("trade.html")

@app.route("/analytics")
def analytics():
    """Examine stock data"""

    # TODO

    return render_template("analytics.html")

@app.route("/account")
def account():
    """Manage Account"""

    # TODO

    return render_template("account.html")

@app.route("/privacy")
def privacy():
    """Display Privacy Policy"""

    return render_template("privacy.html")

# Remove for deployment
if __name__ == '__main__':
    app.run(port=5002)