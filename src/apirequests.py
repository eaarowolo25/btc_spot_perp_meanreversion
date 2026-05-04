import time
import requests
import pandas as pd


#times
end_time = int(time.time()*1000)
start_time = end_time - (3*365*24*60*60*1000)

#Spot Data Pulls
url_spot = "https://api.binance.com/api/v3/klines"

params = {
    "symbol": "BTCUSDT",
    "interval": "1d",
    "startTime": start_time,
    "endTime": end_time,
    "limit": 1000
}

response = requests.get(url_spot, params=params)

data = response.json()

df = pd.DataFrame(data)

df = df.iloc[:, :6]
df.columns = ["timestamp", "open", "high", "low", "close", "volume"]

for col in ["open", "high", "low", "close"]:
    df[col] = df[col].astype(float)

#dataframe to csv
#df.to_csv('raw_btcspot.csv', index=False)


#Future Data Pulls
url_fut = "https://fapi.binance.com/fapi/v1/klines"

response_fut = requests.get(url_fut, params=params)

data_fut = response_fut.json()

df_fut = pd.DataFrame(data_fut)
df_fut = df_fut.iloc[:,:6]
df_fut.columns = ["timestamp", "open", "high", "low", "close", "volume"]

for col in ["open", "high", "low", "close"]:
    df_fut[col] = df_fut[col].astype(float)

#df_fut.to_csv("raw_btcfut.csv", index=False)

#Cleaning the data pulling to csv

df = df.drop(columns=["open", "high", "low"])
df_fut = df_fut.drop(columns=["open", "high", "low"])

df.to_csv("cleaned_btcspot.csv", index = False)
df_fut.to_csv("cleaned_btcfuture.csv", index = False)


df1 = pd.concat([df[["timestamp", "close"]], df_fut[["close"]]], axis=1).copy()
df1.columns = ["timestamp", "spot_price", "future_price"]
df1.to_csv("btcspot_and_future.csv", index = False)

#Change the time in timestamp column to datetime rather than a ms integer