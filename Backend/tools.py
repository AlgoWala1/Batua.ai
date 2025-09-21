import pandas as pd
from requests import get
import yfinance as yf 
import json
from datetime import timedelta, datetime

from constants import *
from utils import *
import data_handlers as dh

### All tools and functions go here 
def orchestrator(instruction, parameters):
    print(parameters)
    response: dict = {}
    if instruction == "stock_price":
        response = get_stock_price(parameters['company_name'], parameters['date'], parameters.get('marker'))
    elif instruction == "time_period":
        response = time_period(parameters['company_name'], parameters['start_date'], parameters['end_date'])
    elif instruction == "time_period_for_benchmark":
        response = time_period_for_benchmark(parameters['benchmark_name'], parameters['start_date'], parameters['end_date'])
    elif instruction == 'top_movers_for_benchmark':
        response = top_movers_for_benchmark(parameters['benchmark_name'], parameters['start_date'], parameters['end_date'], parameters.get('sort_order', 1), parameters.get('top_n', 5))
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
        return ERROR_MESSAGE_BACKEND
    
# company name could have more than one company separated by commas
def time_period(company_name, start_date, end_date):
    try:
        result = []
        companies = [comp.strip() for comp in company_name.split(',')]
        for company in companies:
            print(company)
            stock_name , ticker = dh.match_company_name_with_ticker(company)
            if not ticker:
                return {"error": "Company name could not be resolved"}
            hist = ticker.history(start=start_date, end=end_date)
            move = float(round((hist['Close'].iloc[-1] - hist['Open'].iloc[0])/hist['Open'].iloc[0] * 100, 2))
            if hist.empty:
                return {"error": "No data found for the given date"}
            result.append({
                'company_name': stock_name,
                'Move': f"Gain of {move}%" if move > 0 else f"Loss of {abs(move)}%",
                'High': float(round(hist['High'].max(),2)),
                'Low': float(round(hist['Low'].min(),2)),
                'Start Price': float(round(hist['Open'].iloc[0],2)),
                'End Price': float(round(hist['Close'].iloc[-1],2))
            }
            )
        
        return result
    except Exception as e:
        return ERROR_MESSAGE_BACKEND

# benchmark name could have more than one benchmark separated by commas
def time_period_for_benchmark(benchmark_name, start_date, end_date, ):
    try:
        result = []
        benchmarks = [benchmark.strip() for benchmark in benchmark_name.split(',')]
        for benchmark in benchmarks:
            if benchmark == 'Nifty50':
                benchmark = 'Nifty 50'
            hist, move = get_benchmark_move(benchmark, start_date, end_date)
            if hist.empty:
                return {"error": "No data found for the given date"}
            result.append({
                'benchmark_name': benchmark,
                'Move': f"Gain of {move}%" if move > 0 else f"Loss of {abs(move)}%",
                'High': float(round(hist['High'].max(),2)),
                'Low': float(round(hist['Low'].min(),2)),
                'Start Value': float(round(hist['Open'].iloc[0],2)),
                'End Value': float(round(hist['Close'].iloc[-1],2))
            }
            )
        return result
    except Exception as e:
        return ERROR_MESSAGE_BACKEND
    
def top_movers_for_benchmark(benchmark_name, start_date, end_date, sort_order, top_n):
    try:
        sort_order = int(sort_order)
        top_n = int(top_n)
        if benchmark_name == 'Nifty50':
            benchmark_name = 'Nifty 50'
        if not benchmark_name in BENCHMARKS:
            return {"error": "Benchmark name could not be resolved"}
        _ ,benchmark_move = get_benchmark_move(benchmark_name, start_date, end_date)
        stocks_in_benchmark = BENCHMARKS_TO_STOCKS.get(benchmark_name, NIFTY_50_TICKERS)
        ticker_string = ' '.join(stocks_in_benchmark)
        results = []

        hist = yf.download(tickers = ticker_string, start=start_date, end=end_date, interval = '1d')
        # flatten multi-level columns
        hist.columns = [f"{price}_{ticker}" for price, ticker in hist.columns]
        # for each column calculate move and by open_ticker and close_ticker column first and last values
        for ticker in stocks_in_benchmark:
            try:
                open_price = hist[f'Open_{ticker}'].iloc[0]
                close_price = hist[f'Close_{ticker}'].iloc[-1]
                move = float(round((close_price - open_price)/open_price * 100, 2))
                results.append({
                    'company name': dh.ticker_names_to_company.get(ticker.replace('.NS','')),
                    'Move': move,
                    'Move summary' : f"Gain of {move}%" if move > 0 else f"Loss of {abs(move)}%",
                    'Benchmark comparison': f"Outperformed benchmark by {move - benchmark_move}%" if (move - benchmark_move) > 0 else f"Underperformed benchmark by {abs(move - benchmark_move)}%",
                    'Start Price': float(round(open_price,2)),
                    'End Price': float(round(close_price,2))
                })

            except Exception as e:
                print(e)
                continue
        top_movers = []
        if sort_order == 1:
            top_movers = sorted(results, key=lambda x: x['Move'], reverse=True)[:top_n]
        else:
            top_movers = sorted(results, key=lambda x: x['Move'])[:top_n]
        return top_movers
    except Exception as e:
        return ERROR_MESSAGE_BACKEND

