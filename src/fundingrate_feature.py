import pandas as pd
import requests

df = pd.read_csv("btcspot_and_future.csv")
df = pd.DataFrame(df)

url = "https://fapi.binance.com/fapi/v1/fundingRate"
