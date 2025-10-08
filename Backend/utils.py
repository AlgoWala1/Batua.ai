import yfinance as yf
from datetime import datetime
from constants import *
from cache import cache_lookup

# Helper functions for tools and apis go here

def get_benchmark_move(benchmark, start_date, end_date):
    ticker = yf.Ticker()
    hist = cache_lookup(BENCHMARKS.get(benchmark, "^NSEI"), start_date=start_date, end_date=end_date)
    move = float(round((hist['Close'].iloc[-1] - hist['Open'].iloc[0])/hist['Open'].iloc[0] * 100, 2))
    return hist, move

#Simple Moving averages
def MovingAvg(dataFrame, days):
  Close = dataFrame.Close
  avgDay = sum(Close.iloc[0: days])/days
  return avgDay
  

#exponential moving averages
def ExponenAvg(dataFrame,days):
  multiplier = 2/(days + 1)
  Close = dataFrame.Close
  #use simple moving avg as the first EMA
  #SMA from day = days to 2*days
  EMA = sum(Close[days:2*days])/days
  #loop to find EMA
  for closePrice in Close[0:days][::-1]:
    EMA = closePrice * multiplier + EMA * (1 - multiplier)
  return EMA


def RSIIndex(dataFrame):
  period = 14
  Close = dataFrame['Close'][::-1].reset_index(drop=True)
  delta = Close.diff()
  gain = delta.clip(lower=0)
  loss = -delta.clip(upper=0)
  avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
  avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
  rs = avg_gain / avg_loss
  rsi_series = 100 - 100/(1+rs)
  return float(rsi_series.iloc[-1])
      

def stochastic(dataFrame):
  Close = dataFrame.Close
  Close = Close.iloc[0:20]
  currentClose = dataFrame.Close.iloc[0]
  highestHigh, lowestLow = max(dataFrame.High.iloc[0:14]), min(dataFrame.Low.iloc[0:14])
  stoch_percent = ((currentClose - lowestLow) / (highestHigh - lowestLow)) * 100
  return stoch_percent


def CCI(dataframe):
  dataframe['Typical price'] = (dataframe['High'] + dataframe['Close'] + dataframe['Low'])/3
  # Normalised deviation from 20 days typical mean price value, use scaling factor of 0.015
  scale = 0.015
  SMA_typical_price = float((sum(dataframe['Typical price'].iloc[0:20])/20))
  current_deviation = float(dataframe['Typical price'].iloc[0]) - SMA_typical_price
  dataframe["deviation"] = abs(dataframe['Typical price'] - SMA_typical_price)
  mean_deviation = sum(dataframe["deviation"].iloc[0:20])/20
  cci = current_deviation/(mean_deviation * scale)
  return cci

def volatility(dataframe):
  dataframe['returns'] = dataframe['Close'].iloc[0:252].pct_change()
  vol_1y = dataframe['returns'].std()
  annualised_vol_1y = (252)**0.5 * vol_1y
  return annualised_vol_1y * 100


def get_beta(ticker_symbol):
  df_ticker = cache_lookup(ticker_symbol=ticker_symbol, end_date=datetime.strftime(datetime.today(),"%Y-%m-%d"), days_offset= 4 * 252)
  df_benchmark = cache_lookup(ticker_symbol = BENCHMARKS.get("Nifty 50"), end_date=datetime.strftime(datetime.today(),"%Y-%m-%d"), days_offset= 4 * 252)
  df_ticker['returns'] = df_ticker['Close'].pct_change()
  df_benchmark['returns'] = df_benchmark['Close'].pct_change()
  covariance = df_ticker['returns'].cov(df_benchmark['returns'])
  variance = df_benchmark['returns'].var()
  beta = covariance/variance
  return beta