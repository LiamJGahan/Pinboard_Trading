from helpers import apology, lookup, lookup_overview, update_cards, usd
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from decimal import Decimal

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

# Citation - Harvardx CS50x Finance LiamJGahan
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

# Citation - Harvardx CS50x Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    connection = create_connection()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            connection.close()
            return apology("must enter new username", 400)

        cursor = connection.cursor()
        username = request.form.get("username")
        username_taken = cursor.execute(
            "SELECT username FROM users WHERE username = %s", (username,)
        )
        username_taken = cursor.fetchone()
        cursor.close()

        # Ensure username not taken
        if username_taken:
            connection.close()
            return apology("Username taken", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            connection.close()
            return apology("must enter new password", 400)

        # Ensure re-entered password was submitted
        elif not request.form.get("confirmation"):
            connection.close()
            return apology("must re-enter new password", 400)

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            connection.close()
            return apology("passwords do not match", 400)

        # Add new user to database
        cursor2 = connection.cursor()
        cursor2.execute(
            "INSERT INTO users (username, hash) VALUES (%s, %s)", (request.form.get(
                "username"), generate_password_hash(request.form.get("password")))
        )
        connection.commit()
        cursor2.close()

        connection.close()
        return redirect("/login")

    else:
        connection.close()
        return render_template("register.html")

# index
@app.route("/", methods=["GET", "POST"])
def index():
    """Create and display stock cards"""

    user_id = session.get("user_id")
    card_list = []
    user_prompt = ""

    # Check if user is signed in
    if user_id != None:
        
        connection = create_connection()

        if request.method == "POST":

            symbol = request.form["symbol"].upper()

            # Ensure symbol has been entered
            if not symbol:
                connection.close()
                return apology("Must enter symbol", 400)

            price = lookup(symbol)
            overview = lookup_overview(symbol)

            # Combine the lookups into one
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

        # Get stocks and transactions
        cursor2 = connection.cursor()
        cursor2.execute("SELECT symbol, name, price, timestamp FROM stocks WHERE user_id = %s", (user_id,))
        cards = cursor2.fetchall()
        transactions = cursor2.execute("SELECT symbol, shares, transaction_total FROM transactions WHERE user_id = %s", (user_id,))
        transactions = cursor2.fetchall()
        cursor2.close()

        # Update the index cards if new day
        update_cards(cards, connection)

        if cards:
            for card in cards:

                amount = 0
                total = 0

                # Count user stock
                for transaction in transactions:
                    if transaction["symbol"] == card["symbol"]:
                        amount += transaction["shares"]

                # Sum amount of stock with the latest closing price
                total = card["price"] * amount

                # Create card list
                card_list.append({
                    "symbol": card["symbol"],
                    "name": card["name"],
                    "price": usd(card["price"]),
                    "amount": amount,
                    "total": usd(total)
                })
        else:
            user_prompt = "Your Pinboard is empty, use the search bar above to pin a new card."

        connection.close()

    return render_template("index.html", card_list=card_list, user_prompt=user_prompt)   

# Citation - Harvardx CS50x Finance (used as base, heavily modified)
@app.route("/trade/<symbol>", methods=["GET", "POST"])
def trade(symbol=None):
    """Buy or sell stock"""

    if not symbol or symbol == None:
        return apology("symbol not found", 500)

    symbol = symbol.upper()
    connection = create_connection()

    # Query database for userID
    cursor = connection.cursor()
    user_id = session.get("user_id")
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    # Check if user is null
    if not user:
        connection.close()
        return apology("user not found, login again", 500)
        

    # Get price and user
    cursor2 = connection.cursor()
    cursor2.execute("SELECT price FROM stocks WHERE user_id = %s AND symbol = %s", (user_id, symbol))
    price_row = cursor2.fetchone()
    transactions = cursor2.execute("SELECT symbol, shares, transaction_total FROM transactions WHERE user_id = %s", (user_id,))
    transactions = cursor2.fetchall()
    cursor2.close()

    # Check price
    if price_row is None:
        connection.close()
        return apology("Price not found", 500)

    price = Decimal(price_row["price"])

    if request.method == "POST":

        shares = request.form.get("shares")

        # Ensure shares was submitted
        if not shares:
            connection.close()
            return apology("must provide shares", 400)

        # Ensure shares are intergers
        try:
            int(shares)
        except:
            connection.close()
            return apology("must provide integers for shares", 400)

        # Check user has required funds
        if ((price * Decimal(shares)) > user["cash"]):
            connection.close()
            return apology("not enough funds for purchase", 400)

        # Update db with new cash total
        cursor3 = connection.cursor()
        remainder = Decimal()

        if int(request.form.get("shares")) < 0:

            # loop though owned_stocks to get amount of stock held for symbol
            amount_of_stock = 0

            cursor3.execute(
            "SELECT symbol, SUM(shares) AS shares, AVG(price) AS price, SUM(transaction_total) AS total FROM transactions WHERE user_id = %s GROUP BY symbol HAVING SUM(shares) > 0", (user_id,)
            )
            owned_stocks = cursor3.fetchall()

            for stock in owned_stocks:
                if stock["symbol"] == symbol:
                    amount_of_stock += stock["shares"]

            # Check user has required amount of stock to sell
            if (amount_of_stock < abs(int(shares))):
                cursor3.close()
                connection.close()
                return apology("not enough stock for sale", 400)

            # Subtract stock from db
            remainder = user["cash"] + (price * abs(Decimal(shares)))

            cursor3.execute(
                "INSERT INTO transactions (user_id, shares, symbol, price, transaction_total) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, int(shares), symbol, price, price * abs(Decimal(shares)))
            )

        elif int(shares) > 0:

            # Add stock to db
            remainder = user["cash"] - (price * Decimal(shares))

            cursor3.execute(
                "INSERT INTO transactions (user_id, shares, symbol, price, transaction_total) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, int(shares), symbol, price, -(price * Decimal(shares)))
            )
        
        else:
            cursor3.close()
            connection.close()
            return apology("Must enter a value above or below zero", 400)

        # Update user cash
        cursor3.execute(
            "Update users Set cash = %s Where id = %s", (remainder, user_id)
        )
        connection.commit()
        cursor3.close()

        connection.close()
        return redirect(f"/trade/{symbol}")

    else:

        amount = 0

        # Count user stock
        for transaction in transactions:
            if transaction["symbol"] == symbol:
                amount += transaction["shares"]

        # Sum amount of stock with the latest closing price
        total = price * amount

        connection.close()
        return render_template("trade.html", symbol=symbol, price=usd(price), amount=amount, total=usd(total))


@app.route("/remove_stock/<symbol>", methods=["GET", "POST"])
#@login_required
def remove_stock(symbol=None):

    if not symbol or symbol == None:
        return apology("symbol not found", 500)

    symbol = symbol.upper()
    user_id = session["user_id"]

    if not symbol:
        return apology("Missing symbol", 500)

    connection = create_connection()
    cursor = connection.cursor()

    # Get total shares
    amount_of_stock = 0

    cursor.execute(
    "SELECT symbol, SUM(shares) AS shares, AVG(price) AS price, SUM(transaction_total) AS total FROM transactions WHERE user_id = %s GROUP BY symbol HAVING SUM(shares) > 0", (user_id,)
    )
    owned_stocks = cursor.fetchall()

    for stock in owned_stocks:
        if stock["symbol"] == symbol:
            amount_of_stock += stock["shares"]

    # Sell shares
    if amount_of_stock > 0:

        # Get user
        cursor.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        user = cursor.fetchone()

        # Check if user is null
        if not user:
            connection.close()
            return apology("user not found, login again", 500)

        # Get price
        cursor.execute("SELECT price FROM stocks WHERE user_id = %s AND symbol = %s", (user_id, symbol))
        price_row = cursor.fetchone()

        # Check price
        if price_row is None:
            connection.close()
            return apology("Price not found", 500)

        price = Decimal(price_row["price"])

        remainder = user["cash"] + (price * abs(Decimal(amount_of_stock)))

        # Enter transaction into db
        cursor.execute(
            "INSERT INTO transactions (user_id, shares, symbol, price, transaction_total) VALUES (%s, %s, %s, %s, %s)", 
            (user_id, -int(amount_of_stock), symbol, price, -price * abs(amount_of_stock))
        )

        # Update user cash
        cursor.execute(
            "Update users Set cash = %s Where id = %s", (remainder, user_id)
        )

    # Remove Stock
    cursor.execute(
        "DELETE FROM stocks WHERE user_id = %s AND symbol = %s",
        (user_id, symbol)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return redirect("/")


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