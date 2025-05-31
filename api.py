from helpers import apology, login_required, lookup, lookup_overview, update_cards, usd
from flask import Flask, jsonify, redirect, render_template, request, session
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

# Citation - Harvardx CS50x Finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    connection = create_connection()

    if request.method == "POST":

        username = request.form.get("username")

        # Ensure username was submitted
        if not username:
            connection.close()
            return apology("must enter new username", 400)

        cursor = connection.cursor()
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


@app.route("/check_username", methods=["POST"])
def check_username():
    username = request.json.get("username")

    # Ensure username was submitted
    if not username:
        return jsonify({"available": False}), 400

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    username_taken = cursor.fetchone()
    cursor.close()
    connection.close()

    return jsonify({"available": not bool(username_taken)})

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

                # Get the total stock count for this user
                cursor.execute("SELECT MAX(position) AS max FROM stocks WHERE user_id = %s", (user_id,))
                max = cursor.fetchone()

                # If user has no stocks, start at 1
                next_position = (max["max"] or 0) + 1

                # Check if stock exists, if not, add a new one
                cursor.execute("SELECT * FROM stocks WHERE user_id = %s AND symbol = %s", (user_id, symbol))
                stock = cursor.fetchone()

                if not stock:
                    cursor.execute("""INSERT INTO stocks (user_id, symbol, name, price, industry, description, market_cap, analyst_target,
                    analyst_strong_buy, analyst_buy, analyst_hold, analyst_sell, analyst_strong_sell, position)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", (user_id, card["symbol"], card["name"], card["price"], card["industry"],
                    card["description"], card["market_cap"], card["analyst_target"], card["analyst_strong_buy"], card["analyst_buy"], card["analyst_hold"],
                    card["analyst_sell"], card["analyst_strong_sell"], next_position))
                    connection.commit()

                cursor.close()
            else:
                connection.close()
                return apology("Alphavantage API limit reached", 503)

        # Get stocks and transactions
        cursor2 = connection.cursor()
        cursor2.execute("SELECT symbol, name, price, change, timestamp FROM stocks WHERE user_id = %s ORDER BY position ASC", (user_id,))
        cards = cursor2.fetchall()

        # Update the index cards if new day
        update_cards(cards, connection)

        # Get cards after update
        cursor2.execute("SELECT symbol, name, price, change, timestamp FROM stocks WHERE user_id = %s ORDER BY position ASC", (user_id,))
        cards = cursor2.fetchall()

        # Get transactions
        cursor2.execute("SELECT symbol, shares, transaction_total FROM transactions WHERE user_id = %s", (user_id,))
        transactions = cursor2.fetchall()
        cursor2.close()

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
                    "total": usd(total),
                    "change": card["change"]
                })
        else:
            user_prompt = "Your Pinboard is empty, use the search bar above to pin a new card."

        connection.close()

    return render_template("index.html", card_list=card_list, user_prompt=user_prompt)

# Citation - Harvardx CS50x Finance (used as base, heavily modified)
@app.route("/trade/<symbol>", methods=["GET", "POST"])
@login_required
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
        return render_template("trade.html", symbol=symbol, price=usd(price), amount=amount, total=usd(total), cash=usd(user["cash"]))


@app.route("/remove_stock/<symbol>", methods=["GET", "POST"])
@login_required
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


@app.route("/analytics/<symbol>", methods=["GET", "POST"])
@login_required
def analytics(symbol=None):
    """Examine stock data"""

    # Check symbol
    if not symbol or symbol == None:
        return apology("symbol not found", 500)

    user_id = session["user_id"]

    # Check if user_id is null
    if not user_id:
        return apology("user_id not found, login again", 500)


    connection = create_connection()
    cursor = connection.cursor()

    # Get user
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )
    user = cursor.fetchone()

    # Check if user is null
    if not user:
        connection.close()
        return apology("user not found, login again", 500)

    # Get stock
    cursor.execute("""SELECT name, price, description, market_cap, analyst_target, analyst_strong_buy, analyst_buy, analyst_hold,
                    analyst_sell, analyst_strong_sell, timestamp FROM stocks WHERE user_id = %s AND symbol = %s""", (user_id, symbol))
    stock = cursor.fetchone()

    # Check if stock is null
    if not stock:
        connection.close()
        return apology("stock not found", 500)

    # Get transactions
    transactions = cursor.execute("SELECT shares, transaction_total, transaction_date FROM transactions WHERE user_id = %s AND symbol = %s", (user_id, symbol))
    transactions = cursor.fetchall()
    cursor.close()

    connection.close()

    ratings = [stock["analyst_strong_buy"], stock["analyst_buy"], stock["analyst_hold"], stock["analyst_sell"], stock["analyst_strong_sell"]]
    return render_template("analytics.html", ratings=ratings, stock=stock, cash=usd(user["cash"]), transactions=transactions)


@app.route("/account")
@login_required
def account():
    """Manage Account"""

    user_id = session.get("user_id")
    connection = create_connection()

    # Check user_id not null
    if user_id == None:
        connection.close()
        return apology("Must log in", 400)

    # Get user
    cursor = connection.cursor()
    cursor.execute(
        "SELECT username, cash FROM users WHERE id = %s", (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    return render_template("account.html", username=user["username"], cash=usd(user["cash"]))

@app.route("/username", methods=["GET", "POST"])
@login_required
def username():
    """Change Username"""

    user_id = session.get("user_id")

    # Check user_id not null
    if user_id == None:
        connection.close()
        return apology("Must log in again", 500)

    if request.method == "POST":

        connection = create_connection()

        # Check new username not null
        if not request.form.get("newusername"):
            connection.close()
            return apology("must enter new username", 400)

        # Check new username match
        if request.form.get("newusername") != request.form.get("confirmation"):
            connection.close()
            return apology("new username does not match", 400)

        # Check new password not null
        if not request.form.get("password"):
            connection.close()
            return apology("must enter password", 400)

        # Get user
        cursor = connection.cursor()
        user = cursor.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        user = cursor.fetchone()

        # Check password is correct and user exists
        if not user or not check_password_hash(
            user["hash"], request.form.get("password")
        ):
            cursor.close()
            connection.close()
            return apology("user or password is invalid", 400)

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("newusername"),))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            connection.close()
            return apology("Username already exists", 400)

        # Update username
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET username = %s WHERE id = %s", (request.form.get("newusername"), user_id))
        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/account")

    else:

        return render_template("username.html")

# Citation - Harvardx CS50x Finance LiamJGahan (modified)
@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change Password"""

    user_id = session.get("user_id")

    # Check user_id not null
    if user_id == None:
        return apology("Must log in", 400)

    if request.method == "POST":

        connection = create_connection()

        # Check old password not null
        if not request.form.get("oldpassword"):
            connection.close()
            return apology("must enter old password", 400)

        # Check new password not null
        if not request.form.get("newpassword"):
            connection.close()
            return apology("must enter new password", 400)

        # Check new passwords match
        if request.form.get("newpassword") != request.form.get("confirmation"):
            connection.close()
            return apology("new passwords do not match", 400)

        # Get user
        cursor = connection.cursor()
        user = cursor.execute(
            "SELECT * FROM users WHERE id = %s", (user_id,)
        )
        user = cursor.fetchone()

        # Check password is correct and user exists
        if not user or not check_password_hash(
            user["hash"], request.form.get("oldpassword")
        ):
            cursor.close()
            connection.close()
            return apology("user or old password is invalid", 400)

        # Update password
        hash = generate_password_hash(request.form.get("newpassword"))
        cursor.execute("UPDATE users SET hash = %s WHERE id = %s", (hash, user_id))
        connection.commit()

        cursor.close
        connection.close()

        return redirect("/account")

    else:

        return render_template("password.html")

@app.route("/privacy")
def privacy():
    """Display Privacy Policy"""

    return render_template("privacy.html")


@app.route("/addfunds", methods=["GET", "POST"])
@login_required
def addfunds():
    """Add funds to bank balance"""

    user_id = session.get("user_id")
    connection = create_connection()

    # Check user_id not null
    if user_id == None:
        connection.close()
        return apology("Must log in", 400)

    # Get user
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    # Check user exists
    if not user:
        connection.close()
        return apology("user is invalid", 500)

    if request.method == "POST":

        cash = request.form.get("cash")

        # Check cash are intergers
        try:
            int(cash)
        except:
            connection.close()
            return apology("must provide integers for cash", 400)

        # Check funds not below 0
        if (int(cash) <= 0):
            connection.close()
            return apology("amount must be higher than 0", 400)

        # Sum new balance
        sum = int(cash) + user["cash"]

        # Update cash balance
        cursor2 = connection.cursor()
        cursor2.execute("UPDATE users SET cash = %s WHERE id = %s", (sum, user_id))
        connection.commit()

        cursor2.close()
        connection.close()

        return redirect("/addfunds")

    else:

        connection.close()
        return render_template("addfunds.html", user_cash=usd(user["cash"]))


@app.route('/update_order', methods=['POST'])
@login_required
def update_order():

    user_id = session.get("user_id")
    connection = create_connection()

    # Check user_id not null
    if user_id == None:
        connection.close()
        return apology("Must log in", 400)

    # Check card order not null
    if 'order' not in request.json:
        connection.close()
        return apology("Card order not found", 500)

    # Get card order
    card_order = request.json['order']

    cursor = connection.cursor()

    try:
        # Reorder cards
        for i, symbol in enumerate(card_order, start=1):
            cursor.execute(
                "UPDATE stocks SET position = %s WHERE user_id = %s AND symbol = %s",
                (i, user_id, symbol)
            )
        connection.commit()

        cursor.close()
        connection.close()
        return jsonify({"message": "Card updated"}), 200

    except Exception as e:
        connection.rollback()

        cursor.close()
        connection.close()
        return apology("Card order not saved", 500)

app.jinja_env.filters["usd"] = usd

# Remove for deployment
if __name__ == '__main__':
    app.run(port=5002)
