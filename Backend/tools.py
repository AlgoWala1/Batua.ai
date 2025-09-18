import pandas as pd
from requests import get
import yfinance as yf 
import json
from datetime import timedelta, datetime
import data_handlers as dh
### All tools and functions go here 
def orchestrator(instruction, parameters):
    response: dict = {}
    if instruction == "stock_price":
        response = get_stock_price(parameters['company_name'], parameters['date'], parameters.get('marker'))
    elif instruction == "time_period":
        response = time_period(parameters['company_name'], parameters['start_date'], parameters['end_date'], parameters['is_benchmark'])
    else:
        response =  {"error": "Invalid instruction"}
    return response

def get_stock_price(company_name, date, marker):
    try:
        stock_name , ticker = dh.match_company_name_with_ticker(company_name)
        if not ticker:
            return {"error": "Company name could not be resolved"}
        hist = ticker.history(period="1d", start=date)
        if hist.empty:
            return {"error": "No data found for the given date"}
        closing_price = hist[marker].values[0]
        print(hist)
        return {
            'company_name': stock_name,
            'date': date,
            f"{marker} price": float(round(closing_price,2))
        }
    except Exception as e:
        return {"error": str(e)}
    

def time_period(company_name, start_date, end_date, is_benchmark):
    try:
        stock_name , ticker = dh.match_company_name_with_ticker(company_name)
        if not ticker:
            return {"error": "Company name could not be resolved"}
        hist = ticker.history(start=start_date, end=end_date)
        move = float(round((hist['Close'][-1] - hist['Open'][0])/hist['Open'][0] * 100, 2))
        if hist.empty:
            return {"error": "No data found for the given date"}
        return {
            'company_name': stock_name,
            'Move': f"Gain of {move}%" if move > 0 else f"Loss of {abs(move)}%",
            'High': float(round(hist['High'].max(),2)),
            'Low': float(round(hist['Low'].min(),2)),
            'Start Price': float(round(hist['Open'][0],2)),
            'End Price': float(round(hist['Close'][-1],2))
        }
    except Exception as e:
        return {"error": str(e)}
    pass
