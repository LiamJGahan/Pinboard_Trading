from flask import redirect, render_template, session
from functools import wraps
from dotenv import load_dotenv
import os
import requests

load_dotenv()
api_key = os.getenv('ALPHAVANTAGE_KEY')

def lookup(symbol):
    """Look up the latest stock price."""
    
    price_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol.upper()}&interval=5min&apikey={api_key}"
    try:
        response = requests.get(price_url)
        response.raise_for_status()
        quote_data = response.json()

        # Get the recent closing price
        time_series = quote_data.get("Time Series (5min)", {})
        last_time = next(iter(time_series))
        price = last_time["4. close"]
        return {
            "price": price,
            "symbol": symbol.upper()
        }
                  
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    
    return None

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
        market_cap = company.get("MarketCapitalization", "N/A")
        # might add these:
        #"AnalystTargetPrice",
        #"AnalystRatingStrongBuy",
        #"AnalystRatingBuy",
        #"AnalystRatingHold",
        #"AnalystRatingSell",
        #"AnalystRatingStrongSell",
        return {
            "name": company_name,
            "industry": industry,
            "description": description,
            "market_cap": market_cap,
            "symbol": symbol.upper()
        } 
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    
    return None