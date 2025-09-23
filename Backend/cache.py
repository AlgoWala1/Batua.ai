import time
import yfinance as yf
from datetime import timedelta, datetime
# cache ticker data or other in use data items here

TICKER_DATA = {}
CACHE_EXPIRY_TIME = 600
MAX_CACHE_SIZE = 500
last_cache_entry: time 

def cache_lookup(ticker_symbol, start_date = None, end_date = None, days_offset : int = None):
    global TICKER_DATA, CACHE_EXPIRY_TIME, MAX_CACHE_SIZE, last_cache_entry
    currTime = time.time()
    if (len(TICKER_DATA) and ((currTime - last_cache_entry) > CACHE_EXPIRY_TIME)) or (len(TICKER_DATA) > MAX_CACHE_SIZE):
        # empty 
        TICKER_DATA = {}
    
    if days_offset: 
        if start_date:
            end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=days_offset - 1)).strftime("%Y-%m-%d")
        else:
            start_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=days_offset)).strftime("%Y-%m-%d")
    
    # convention to include end date in many cases
    end_date = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    if ticker_symbol not in TICKER_DATA:
        print("Cache Miss")
        hist = yf.Ticker(ticker_symbol).history(start = start_date, end = end_date)
        if len(TICKER_DATA) == 0:
            last_cache_entry = currTime
        result = hist
        TICKER_DATA[ticker_symbol] = {'time': currTime, 'data': hist, 'start_date':start_date, 'end_date':end_date}
    
    else:
        cache = TICKER_DATA[ticker_symbol]
        print("Cache hit")
        # cache hit, use stored data
        if start_date >= cache['start_date'] and end_date <= cache['end_date']:
            print("Overlap")
            hist = cache['data']
        else:
            # partial overlap
            print("Partial overlap")
            fetch_st = min(start_date, cache['start_date'])
            fetch_end = max(end_date, cache['end_date'])
            hist = yf.Ticker(ticker_symbol).history(start = fetch_st, end = fetch_end)
            TICKER_DATA[ticker_symbol] = {'time': cache['time'], 'data': hist, 'start_date':start_date, 'end_date':end_date}
            hist = hist[(hist.index >= start_date) & (hist.index < end_date)]
        

    return hist

            



