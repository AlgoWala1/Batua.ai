import pandas as pd
from fuzzywuzzy import process
import yfinance as yf
import logging as log
company_names: list = []
company_names_to_ticker: dict = {}

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
    global company_names, company_names_to_ticker
    df = pd.read_csv('EQUITY_L.csv')
    print("Read csv")
    company_names = df['NAME OF COMPANY'].tolist()
    company_names_to_ticker = df.set_index('NAME OF COMPANY')['SYMBOL'].to_dict()
    
