import datetime
from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv
import os
import requests
from decimal import Decimal

load_dotenv()
api_key = os.getenv('ALPHAVANTAGE_KEY')

# Citation - Harvardx CS50x Finance
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

# Citation - Harvardx CS50x Finance
def login_required(f):
    
    """Decorate routes to require login."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# Citation - Harvardx CS50x Finance
def lookup(symbol):
    """Look up the latest stock price."""
    
    price_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol.upper()}&interval=5min&apikey={api_key}"
    try:
        response = requests.get(price_url)
        response.raise_for_status()
        quote_data = response.json()

        # Get the recent closing price
        time_series = quote_data.get("Time Series (5min)", {})
        if time_series: 
            last_time = next(iter(time_series))
            price = time_series[last_time]["4. close"]
            return {
                "price": price,
                "symbol": symbol.upper()
            }
                  
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    
    return None

# Citation - Harvardx CS50x Finance
def lookup_overview(symbol):

    """Look up company information."""
    
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol.upper()}&apikey={api_key}"

    try:
        response = requests.get(overview_url)
        response.raise_for_status()
        company = response.json()

        # Getting the company information
        company_name = company.get("Name", "N/A")
        industry = company.get("Industry", "N/A")
        description = company.get("Description", "No description available.")
        market_cap = company.get("MarketCapitalization", "0")
        analyst_target = company.get("AnalystTargetPrice", "0")
        analyst_strong_buy = company.get("AnalystRatingStrongBuy", "0")
        analyst_buy = company.get("AnalystRatingBuy", "0")
        analyst_hold = company.get("AnalystRatingHold", "0")
        analyst_sell = company.get("AnalystRatingHold", "0")
        analyst_strong_sell = company.get("AnalystRatingHold", "0")
        return {
            "name": company_name,
            "industry": industry,
            "description": description,
            "market_cap": market_cap,
            "symbol": symbol.upper(),
            "analyst_target": analyst_target,
            "analyst_strong_buy" : analyst_strong_buy,
            "analyst_buy": analyst_buy,
            "analyst_hold": analyst_hold,
            "analyst_sell": analyst_sell,
            "analyst_strong_sell": analyst_strong_sell,
        } 
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    
    return None

def update_cards(rows, connection):

    if not rows:
        return # No card_list
    
    user_id = session.get("user_id")

    if user_id == None:
        connection.close()
        return apology("Must log in", 400)

    for stock in rows:
        if stock["timestamp"].date() != datetime.datetime.now().date():
            
            price = lookup(stock["symbol"])
            overview = lookup_overview(stock["symbol"])
            change = 0


            if price and overview:
                updated_card = {**price, **overview, "timestamp": datetime.datetime.now()}
                new_price = updated_card["price"]

                cursor = connection.cursor()

                # Fetch current stock for price comparison
                cursor.execute("SELECT price FROM stocks WHERE user_id = %s AND symbol = %s", (user_id, stock["symbol"]))
                current_stock = cursor.fetchone()

                if current_stock["price"] is not None:
                    old_price = current_stock["price"]  
                else: 
                    old_price = new_price

                # Calculate the price change
                if Decimal(new_price) > old_price:
                    change = 1
                elif Decimal(new_price) < old_price:
                    change = -1
                else:
                    change = 0

                cursor.execute("""UPDATE stocks SET name = %s, price = %s, industry = %s, description = %s, 
                               market_cap = %s, timestamp = %s, analyst_target = %s, analyst_strong_buy = %s, analyst_buy = %s
                               , analyst_hold = %s ,analyst_sell = %s, analyst_strong_sell = %s, change = %s WHERE user_id = %s AND symbol = %s""", 
                (
                    updated_card["name"],
                    updated_card["price"],
                    updated_card["industry"],
                    updated_card["description"],
                    updated_card["market_cap"],
                    updated_card["timestamp"],
                    updated_card["analyst_target"],
                    updated_card["analyst_strong_buy"],
                    updated_card["analyst_buy"],
                    updated_card["analyst_hold"],
                    updated_card["analyst_sell"],
                    updated_card["analyst_strong_sell"],
                    change,
                    user_id,
                    stock["symbol"]
                ))
                connection.commit()

                cursor.close()

# Citation - Harvardx CS50x Finance
def usd(value):
    """Format value as USD."""

    return f"${value:,.2f}"