import yfinance as yf
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

# def CalcBeta(dataFrame):
#   nifty = pd.read_csv("NIFTY50.csv")
#   auto = pd.read_csv("^CNXAUTO.csv").sort_values(by = ["Close"],ascending=False,ignore_index=True)
#   nifty.rename(columns = {" Close":"Nifty"},inplace = True)
#   auto.rename(columns = {"Close":"AutoNifty"},inplace = True)
#   closings = pd.concat([dataFrame["Date"],nifty["Nifty"],auto["AutoNifty"],dataFrame["Close"]],axis = "columns")
#   print("\n")
#   print("Closing prices of stock with Nifty and Nifty Auto")
#   print(closings.head())
#   closings.dropna(inplace = True)
#   NiftyRet = []
#   StockRet = []
#   AutoRet = []
#   #produce a 2 year weekly analysis
#   for week in range(104,0,-1):
#     NiftyRet.append((nifty.Nifty[(week-1)*7] - nifty.Nifty[week*7]) * 100/nifty.Nifty[week*7])
#     AutoRet.append((auto.AutoNifty[(week-1)*7] - auto.AutoNifty[week*7]) * 100/auto.AutoNifty[week*7])
#     StockRet.append((dataFrame.Close[(week-1)*7] - dataFrame.Close[week*7]) * 100/dataFrame.Close[week*7])
#   mapping = {"NiftyReturns":[],"AutoNiftyReturns":[],"StockReturns":[]}
#   for week in range(0,103):
#     mapping["NiftyReturns"].append(NiftyRet[week])
#     mapping["StockReturns"].append(StockRet[week])
#     mapping["AutoNiftyReturns"].append(AutoRet[week])
#   dataFrame = pd.DataFrame(mapping)
#   X = dataFrame[["NiftyReturns"]]
#   linearModel = LinearRegression()
#   linearModel.fit(X,dataFrame["StockReturns"])
#   print()
#   print("A 104 week Beta analysis")
#   niftyBeta = round(linearModel.coef_[0],3)
#   print("Beta value with regards to Nifty Index",niftyBeta)
#   X = dataFrame[["AutoNiftyReturns"]]
#   linearModel.fit(X,dataFrame["StockReturns"])
#   auto = round(linearModel.coef_[0],3)
#   print("Beta values with regards to Auto Nifty Index",auto)
#   if (niftyBeta+auto)/2 < 0:
#     print("Stock performs opposite to market")
#   elif (niftyBeta + auto)/2 < 1:
#     print("Stock moves slower than the market in the same direction")
#   else:
#     print("Stock moves faster than the market in the same direction")
#   print("\n")