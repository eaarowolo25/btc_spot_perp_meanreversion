#!/usr/bin/env python
# coding: utf-8

# # Mean Reversion BTC Futures vs Spot

# ## Import libraries

# In[24]:


import time
import pandas as pd
import numpy as np
import requests
import matplotlib as mp


# ## Pulling Data from Binance API

# In[25]:


#spot data

url_spot = "https://api.binance.com/api/v3/klines"

end_time = int(time.time()*1000)

start_time = end_time - (3*365*24*60*60*1000)

params = {
    "symbol" : "BTCUSDT",
    "interval" : "1d",
    "startTime" : start_time,
    "endTime" : end_time,
    "limit" : 1000
}

response = requests.get(url_spot, params=params)

data = response.json()

print(type(data))
print(len(data))
print(data[0])


# In[ ]:


#Cleaning data
df = pd.DataFrame(data)

df = df.iloc[:,:6]
df.columns = ["timestamp", "open", "high", "low", "close", "volume"]

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

for col in ["open", "high", "low", "close"]:
    df[col] = df[col].astype(float)

df.head()


# In[ ]:


#Futures Data
url_fut = "https://fapi.binance.com/fapi/v1/klines"

response_fut = requests.get(url_fut, params=params)

data_fut = response_fut.json()

print(type(data_fut))
print(data_fut[0])


# In[ ]:


#cleaning futures data

df_fut = pd.DataFrame(data_fut) #puts the list into a dataframe

df_fut = df_fut.iloc[:,:6] #selects only the first 6 columns
df_fut.columns = ["timestamp", "open", "high", "low", "close", "volume"] #naming the columns

df_fut["timestamp"] = pd.to_datetime(df_fut["timestamp"], unit="ms") #changes the time from ms to date and ms 

for col in ["open", "high", "low", "close"]:
    df_fut[col] = df_fut[col].astype(float) #changes the numbers from string into float

df_fut.head()


# ## Cleaning Data

# In[29]:


df = df.drop("high", axis=1) # axis 0=row, 1=column
df = df.drop("low", axis=1) #deleting columns individually

df.head()


# In[ ]:


df = df.drop(columns=["high", "low"], axis=1)

df.head()


# In[ ]:


df_fut = df_fut.drop(columns=["open", "high", "low"], axis=1) #deleting multiple columns in one line

df_fut.head()


# In[ ]:


#checking if the timestamps are identical
is_identical = df["timestamp"].equals(df_fut["timestamp"])

print(f"Are the timestamps identical? {is_identical}")


# In[ ]:


#Renaming the columns
df.columns = ["timestamp", "spot_price", "volume"]
df_fut.columns = ["timestamp", "fut_price", "volume"]


# In[ ]:


#aligning all columns from future price and spot price to one dataframe
#use of concatenate to do this

df1 = pd.concat([df[["timestamp", "spot_price"]],df_fut[["fut_price"]]], axis=1).copy()

df1.head()


# The code works because there is nothing missing, but if there is a timestamp duplication or a price missing for a timestamp, it falls apart. 
# 
# This is something to work on to improve this code

# ## Visuallising data

# In[31]:


import matplotlib.pyplot as plt


x = df1["timestamp"]
#plt.xticks(rotation=45)

y1 = df1["fut_price"]

y2 = df1["spot_price"]


fig, ax = plt.subplots()

ax.plot(x, y1, label="Futures Price")
ax.plot(x, y2, label="Spot Price")


ax.set_xlabel("time")

ax.set_ylabel("price (USD)")

ax.set_title("BTCUSDT Spot vs Futures Price")

ax.legend()
plt.xticks(rotation=45)

plt.show()


# ## Feature Creation

# ### Feature Creation - Spread & Spread PCT and then plotting

# In[142]:


spread = df1["spot_price"] - df1["fut_price"]

spread_pct = spread / df1["spot_price"]


# In[ ]:


#plotting spread

y3 = spread

y4 = spread_pct

fig, ax = plt.subplots()
ax.plot(x, y3, label="Spread")
#ax.plot(x, y4, label="Spread Percentage")

ax.set_xlabel("Time")
ax.set_ylabel("Spread (USD)")
ax.set_title("BTC Future to Spot Spread")

ax.legend()
plt.xticks(rotation=45)

plt.show()


# ### Feature Creation & Plotting - rolling_mean, rolling_std & z score

# In[143]:


rolling_mean = spread_pct.rolling(window=20).mean()
rolling_std = spread_pct.rolling(window=20).std()

z_score = (
    (spread_pct - rolling_mean) /
    rolling_std
)


# In[ ]:


#plotting spread z score

y5 = z_score


fig, ax = plt.subplots()
ax.plot(x, y5, label="Spread")


ax.set_xlabel("Time")
ax.set_ylabel("Zscore")
ax.set_title("BTC Future to Spot Spread Z-Score")

ax.legend()
plt.xticks(rotation=45)

plt.show()


# ### Feature Creation - funding rate

# Getting Raw Data

# In[156]:


print(start_time)


# In[161]:


import requests
import pandas as pd

url = "https://fapi.binance.com/fapi/v1/fundingRate"

all_data = []
current_start = start_time

while current_start < end_time:
    paramsf = {
        "symbol": "BTCUSDT",
        "startTime": current_start,
        "endTime": end_time,
        "limit": 1000
    }

    responsef = requests.get(url, params= paramsf)

    dataf = responsef.json()

    if not dataf:
        break

    all_data.extend(dataf)

    last_time = dataf[-1]["fundingTime"]
    current_start = last_time + 1

    print(f"Pulled up to: {pd.to_datetime(last_time, unit='ms')}")

    time.sleep(0.1)

funding_df = pd.DataFrame(all_data)

funding_df.head()



# Cleaning funding data

# In[162]:


funding_df["fundingRate"] = funding_df["fundingRate"].astype(float)
funding_df["fundingTime"] = pd.to_datetime(funding_df["fundingTime"], unit="ms")

funding_df =funding_df.rename(columns={
    "fundingTime": "timestamp",
    "fundingRate": "funding_rate"
})
funding_df.head()


# In[166]:


funding_df = funding_df.sort_values("timestamp")

funding_df


# ### Clean Feature adding to one data set

# In[78]:


df1["spread"] = df1["spot_price"] - df1["fut_price"]
df1["spread_pct"] = df1["spread"]/df1["spot_price"]
df1["rolling_mean"] = df1["spread_pct"].rolling(20).mean()
df1["rolling_std"] = df1["spread_pct"].rolling(20).std()

df1["zscore"] = (
    (df1["spread_pct"] - df1["rolling_mean"]) / df1["rolling_std"]
)

df1.head()

#Always keep features within one big dataset thet they're derived from


# Adding funding to the dataset

# In[208]:


funding_df


# In[216]:


funding_df["timestamp"] = funding_df["timestamp"].dt.floor("D")

funding_df["date"] = (
    funding_df["timestamp"].dt.date
)

daily_funding = (
    funding_df
    .groupby("date")["funding_rate"]
    .sum()
    .reset_index()
)

daily_funding = daily_funding.rename(columns={"funding_rate":"daily_funding"})
#funding_df = funding_df.drop(columns=["markPrice"])

#funding_df.head()
"""
df1 = stats_df.merge(
    funding_df,
    on="date",
    how="left"
)
"""
daily_funding


# In[219]:


stats_df["date"] = (
    stats_df["timestamp"].dt.date
)

stats_df = stats_df.merge(
    daily_funding,
    on="date",
    how="left"
)


# In[220]:


stats_df.head()


# In[177]:


stats_df = df1.copy()

stats_df = stats_df.drop(columns=["symbol_x", "symbol_y", "funding_rate_y"])

stats_df.head()


# In[ ]:


#moving funding rate to the 4th column
col = stats_df.pop("funding_rate_x")
stats_df.insert(3, "funding_rate", col)

stats_df.head()


# ## Signal Creation and Analysis

# In[73]:


#print(z_score)
df_z = pd.DataFrame(z_score)
df_z.columns = ["zscore"]


stats_df = pd.concat([df1["timestamp"], df_z["zscore"]], axis=1).copy()

short_signal = z_score > 2
long_signal = z_score < -2

long_count = (stats_df["zscore"]<-1).sum()
print(long_count)

short_count = (stats_df["zscore"] > 1).sum()
print(short_count)

total = len(stats_df)

long_freq = long_count/total
short_freq = short_count/total

print(long_freq)
print(short_freq)


# ### Creating short and long signals

# In[95]:


short_signal = (stats_df["zscore"]>1) & (stats_df["zscore"].shift(1) <= 1)
short_events = short_signal.sum()

long_signal = (stats_df["zscore"]<-1) & (stats_df["zscore"].shift(1) >=-1)
long_events = long_signal.sum()

print(long_events)
print(short_events)


# In[ ]:


#analysis of signals per month

#First aligning all short signals with their respective date
short_df = pd.DataFrame({"timestamp": stats_df["timestamp"],
                         "shortsig": short_signal})

#short_df.head()

#Timestamped short signals
display(short_df.loc[(short_df["shortsig"]==True)])


# In[ ]:


#Understanding the number of short signals per month

short_df = stats_df.loc[short_signal].copy()

short_df["month"] = short_df["timestamp"].dt.to_period("M")

monthly_counts = short_df.groupby("month").size()

print(monthly_counts)


# Understanding the nature of the mean reversion

# In[77]:


#Lists each entry point as short_signal is boolean so it provides timestamp for every true entry
signal_indices = stats_df.index[short_signal]

holding_periods = []

for idx in signal_indices:
    future_data = stats_df.loc[idx+1:]

    reversion = future_data[future_data["zscore"]<=0]

    if not reversion.empty:
        t1 = reversion.index[0]
        holding_period = t1-idx
        holding_periods.append(holding_period)

print("Average days to mean revert:", np.mean(holding_periods))
print("Median:", np.median(holding_periods))
print("Max:", np.max(holding_periods))


# ### Signal Creation including funding rate

# In[185]:


short_signalf = (
    (stats_df["zscore"] > 1) &
    (stats_df["funding_rate"] > 0)
)

long_signalf = (
    (stats_df["zscore"] <-1) &
    (stats_df["funding_rate"] < 0)
)


# ### First PNL Creation - done wrong 
# Adding PNL to understand the mean reversion visually and numerically

# In[91]:


#pnl = entry_spread - current_spread

trades = []

for idx in signal_indices:
    entry_row = stats_df.loc[idx]
    entry_spread = entry_row["spread_pct"]

    future_data = stats_df.loc[idx+1:].copy()

    reversion = future_data[future_data["zscore"] <=0]

    trade = {}

    if not reversion.empty:
        t1 = reversion.index[0]
        trade_data = stats_df.loc[idx:t1].copy()
        reverted = True
    else:
        #trade doesn't revert, allow it to take the full path
        trade_data = stats_df.loc[idx:].copy()
        t1 = trade_data.index[-1]
        reverted = False

    holding_period = (
        stats_df.loc[t1, "timestamp"] - entry_row["timestamp"]
    ).days

    #pnl path
    trade_data["pnl"] = entry_spread - trade_data["spread_pct"]


    #final pnl
    final_pnl = trade_data["pnl"].iloc[-1]

    trade["entry_idx"] = idx
    trade["exit_idx"] = t1
    trade["holding_period"] = holding_period
    trade["final_pnl"] = final_pnl
    trade["reverted"] = reverted
    trade ["pnl_path"] = trade_data["pnl"].values

    trades.append(trade)






# In[92]:


trades_df = pd.DataFrame(trades)

trades_df.head()

trade_data.head()


# In[82]:


trades_df["final_pnl"].hist()
trades_df["holding_period"].hist()


# In[83]:


trades_df.groupby("reverted")["final_pnl"].mean()


# In[84]:


plt.figure(figsize=(10,6))

for trade in trades:
    plt.plot(trade["pnl_path"], alpha=0.3)

plt.axhline(0, linestyle="--") #this shows breakeven line
plt.title("Pnl Paths for All Trades")
plt.xlabel("Time Steps")
plt.ylabel("PnL")
plt.show()


# In[85]:


trades_df["returns"] = trades_df["final_pnl"]

initial_capital = 1000

equity = [initial_capital]

for r in trades_df["returns"]:
    new_equity = equity[-1] * (1+r)
    equity.append(new_equity)


# In[86]:


plt.plot(equity)
plt.title("Equity Curve")
plt.xlabel("Trade Number")
plt.ylabel("Equity ($)")
plt.show()


# ## PNL Creation

# In[98]:


stats_df.head()


# # Trading zscore

# ## Trading Logic and Backtest

# In[99]:


#building trading logic
#building the position column
stats_df["positions"] = 0

current_pos = 0

positions = []

for i in range(len(stats_df)):
    z = stats_df["zscore"].iloc[i]

    #entry
    if current_pos == 0:
        if z > 1:
            current_pos = -1
        elif z < -1:
            current_pos = 1

    #exit
    elif current_pos == -1 and z <= 0:
        current_pos = 0
    elif current_pos == 1 and z >= 0:
        current_pos = 0

    positions.append(current_pos)

stats_df["positions"] = positions


# In[102]:


stats_df


# In[104]:


stats_df["spot_return"] = stats_df["spot_price"].pct_change()
stats_df["fut_return"] = stats_df["fut_price"].pct_change()


# In[105]:


stats_df


# In[106]:


stats_df["strategy_returns"] = (
    stats_df["positions"].shift(1) *
    (stats_df["spot_return"] - stats_df["fut_return"])
)


# In[107]:


stats_df


# ### Adding Equity
# Numerically visualising pnl

# In[120]:


initial_cap = 10000

stats_df["equity"] = (
    (1 + stats_df["strategy_returns"].fillna(0))
    .cumprod() * initial_cap
)


# In[118]:


stats_df


# ## Visualising backtest

# In[111]:


plt.figure(figsize=(10,5))
plt.plot(stats_df["timestamp"], stats_df["positions"])
plt.title("Position Over Time")
plt.show()


# In[113]:


plt.figure(figsize=(10,5))
plt.plot(stats_df["timestamp"], stats_df["equity"])
plt.title("PnL From $10k")
plt.xlabel("Time")
plt.ylabel("Equity ($)")
plt.show()


# Performance Metrics

# In[ ]:


"""
To complete

1. The performance stats - cumulative returns, sharpe ratio, max drawdown, win rate

2. Add funding rates

3. Rebuild everything on the 1hr time level -  need to add loop to get through the 1000 rate limit

4. Add slippage and transaction costs

5. Build this to trade incoming data and have this running for 24hrs and see how it does

6. Rewrite everything with more optimised code
"""



# ## Performance Metrics

# In[124]:


#pnl
stats_df["pnl"] = stats_df["equity"] - initial_cap

plt.figure(figsize=(10,5))
plt.plot(stats_df["timestamp"], stats_df["pnl"], label="pnl")
plt.title("PnL over Time")
plt.xlabel("Time")
plt.ylabel("PnL ($)")
plt.show()


# In[128]:


#cumulative return
initial_capital = 10000
stats_df["cumulative_return"] = stats_df["equity"] / initial_capital

stats_df


# In[130]:


stats_df["cumulative_return_pct"] = (stats_df["cumulative_return"] - 1)*100

stats_df


# In[133]:


import numpy as np
#sharpe ratio
returns = stats_df["strategy_returns"].dropna()

sharpe = returns.mean() / returns.std()

sharpe = sharpe * np.sqrt(365)

print("Sharpe Ratio:", sharpe)


# Sharpe is high because the reeturns are tiny but the volatility is even tinier. The spread cancels out because of the market neutral nature of the trade. It completely cancels out the market direction and most of the volatility so the sharp looks amazing

# In[137]:


#max drawdown
equity = stats_df["equity"]

rolling_max = equity.cummax()

drawdown = (equity - rolling_max)/ rolling_max


max_drawdown = drawdown.min()

print("Max drawdown:", max_drawdown)

plt.plot(drawdown)
plt.title("Drawdown")
plt.show()


# In[139]:


#win rate
win_rate = (trades_df["final_pnl"] > 0).mean()

print("Win rate:", win_rate)


# In[140]:


print(stats_df["spot_return"].std())
print(stats_df["fut_return"].std())
print((stats_df["spot_return"] - stats_df["fut_return"].std()))


# In[141]:


stats_df


# # Trading zscore & funding rate

# ## Trading Logic and Backtest

# In[221]:


statsf_df = stats_df.copy()


# In[222]:


statsf_df


# In[223]:


#cleaning up the columns in the new dataframe for a rebuild

col_to_drop = [
    "positions",
    "spot_return",
    "fut_return",
    "strategy_returns",
    "equity",
    "cumulative_return",
    "pnl",
    "cumulative_return_pct"
]

statsf_df = statsf_df.drop(columns= col_to_drop, errors="ignore")
statsf_df.head()



# In[228]:


statsf_df = statsf_df.drop(
    columns=["funding_rate"]
)


# In[229]:


statsf_df.head()


# In[230]:


col = statsf_df.pop("date")
statsf_df.insert(3, "date", col)


# In[231]:


col = statsf_df.pop("daily_funding")
statsf_df.insert(4, "daily_funding", col)


# In[232]:


statsf_df.head()


# In[233]:


#position column
statsf_df["position"] = 0


# In[234]:


#trading logic

current_position = 0

for i in range(len(statsf_df)):
    z = stats_df["zscore"].iloc[i]

    #entry
    if current_position == 0:
        if short_signalf.iloc[i]:
            current_position = -1
        elif long_signalf.iloc[i]:
            current_position = 1

    #exit
    elif current_position == -1:
        if z <= 0:
            current_position = 0
    elif current_position == 1:
        if z >= 0:
            current_position = 0

    #store position
    statsf_df.loc[i, "position"] = current_position


# In[236]:


#building leg returns

statsf_df["spot_return"] = (
    statsf_df["spot_price"].pct_change()
)

statsf_df["fut_return"] = (
    statsf_df["fut_price"].pct_change()
)


# In[237]:


#building spread return
statsf_df["spread_return"] = (
    statsf_df["fut_return"] -
    statsf_df["spot_return"]
)


# In[239]:


#building funding pnl
statsf_df["funding_pnl"] = (
    -statsf_df["position"].shift(1) *
    statsf_df["daily_funding"]
)


# In[240]:


# building price pnl
statsf_df["price_pnl"] = (
    statsf_df["position"].shift(1) *
    statsf_df["spread_return"]
)


# In[241]:


# building strategy return
statsf_df["strategy_return"] = (
    statsf_df["funding_pnl"] +
    statsf_df["price_pnl"]
)


# In[242]:


# building equity
starting_capital = 10000
statsf_df["equity"] = (
    starting_capital *
    (1 + statsf_df["strategy_return"]).cumprod()
)


# ## Visualising Backtest

# In[243]:


#Plotting equity

plt.figure(figsize=(10,5))
plt.plot(statsf_df["timestamp"], statsf_df["equity"], label="equity")
plt.title("Equity over time")
plt.xlabel("Time")
plt.ylabel("Equity ($)")
plt.show()


# In[244]:


#Plotting positions

plt.figure(figsize=(10,5))
plt.plot(statsf_df["timestamp"], statsf_df["position"])
plt.title("Positions over time")
plt.ylabel("Positions")
plt.show()


# ### Performance Metric Analysis

# In[245]:


#total funding contribution to pnl

statsf_df["funding_pnl"].sum()

#pd.set_option("display.float_format", "{:.10f}".format)


statsf_df


# In[246]:


statsf_df["spot_price"].pct_change().head(20)


# In[247]:


statsf_df["spot_return"].abs().max()

