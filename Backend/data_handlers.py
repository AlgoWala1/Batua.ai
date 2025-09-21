import pandas as pd
from fuzzywuzzy import process
import yfinance as yf
import logging as log
import psycopg2
### All data handling functions and variables go here

company_names: list = []
company_names_to_ticker: dict = {}
ticker_names_to_company: dict = {}
Postgresconnection = None 

def init_postgres_connection():
    global Postgresconnection
    try:
    #     Postgresconnection = psycopg2.connect(
    #         host="",
    #         database="",
    #         user="",
    #         password=""
    #     )
        log.info("PostgreSQL connection established")
    except Exception as e:
        log.error(f"Error connecting to PostgreSQL: {e}")
        Postgresconnection = None

def match_company_name_with_ticker(company : str):
    matched_name, score = process.extractOne(company, company_names)
    ticker_symbol = company_names_to_ticker.get(matched_name) + ".NS"
    ticker = yf.Ticker(ticker_symbol)
    if score >= 70:
        return matched_name, ticker 
    else:
        # case where name could not be resolved
        return None, None
    
def init_ticker_dict():
    global company_names, company_names_to_ticker, ticker_names_to_company
    df = pd.read_csv('EQUITY_L.csv')
    print("Read csv")
    company_names = df['NAME OF COMPANY'].tolist()
    company_names_to_ticker = df.set_index('NAME OF COMPANY')['SYMBOL'].to_dict()
    ticker_names_to_company = df.set_index('SYMBOL')['NAME OF COMPANY'].to_dict()
    
