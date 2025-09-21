#Keep common use helper functions here
import yfinance as yf
from constants import *
def get_benchmark_move(benchmark, start_date, end_date):
    ticker = yf.Ticker(BENCHMARKS.get(benchmark, "^NSEI"))
    hist = ticker.history(start=start_date, end=end_date)
    move = float(round((hist['Close'].iloc[-1] - hist['Open'].iloc[0])/hist['Open'].iloc[0] * 100, 2))
    return hist, move