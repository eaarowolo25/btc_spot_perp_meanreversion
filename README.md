README.md
# Project 1: BTC Spot vs Perpetual Futures Mean Reversion

## Objective

Build a systematic trading model that captures **mean reversion in the spread between Bitcoin spot and perpetual futures prices**.

This project simulates a **relative value / basis trading strategy**, similar to what is used in professional trading environments.

---

## Strategy Overview

We model the relationship between:

- Spot price: BTCUSDT (spot market)
- Futures price: BTCUSDT perpetual contract

### Core Idea

The spread between futures and spot:

Spread = Futures Price − Spot Price

or

Spread (%) = (Futures − Spot) / Spot

This spread tends to **mean revert** due to:
- Arbitrage activity
- Funding rate mechanics
- Market positioning

---

## Data Sources

Use public API endpoints:

### Spot Data
https://api.binance.com/api/v3/klines


### Futures Data

https://fapi.binance.com/fapi/v1/klines

---

## Data Requirements

- Symbol: BTCUSDT
- Interval: 1h or 1d
- History: ~3 years (or max available)

---

## Step 1: Data Collection

Pull OHLCV data for both:
- Spot BTCUSDT
- Perpetual BTCUSDT

Ensure:
- Same timestamp frequency
- Proper datetime conversion
- Clean numeric types

---

## Step 2: Data Alignment

Merge datasets on timestamp:

- Inner join on time
- Ensure both series are aligned
- Drop missing values

---

## Step 3: Feature Engineering

### Compute Spread
spread = futures_price - spot_price
spread_pct = spread / spot_price

---

### Compute Rolling Statistics
rolling_mean = spread_pct.rolling(window=20).mean()
rolling_std = spread_pct.rolling(window=20).std()

---

### Compute Z-Score
z_score = (spread_pct - rolling_mean) / rolling_std

---

## Step 4: Trading Logic

Mean reversion strategy:

| Condition            | Position                          |
|---------------------|----------------------------------|
| z_score > +1        | Short futures / Long spot         |
| z_score < -1        | Long futures / Short spot         |
| otherwise           | No position                       |

---

## Step 5: Backtesting

### Returns Calculation
strategy_returns = position.shift(1) * spread_change

Alternative:
- Model PnL based on both legs separately

---

### Performance Metrics

Evaluate:

- Cumulative returns
- Sharpe ratio
- Max drawdown
- Win rate

---

## Step 6: Visualisation

Plot:

- Spread over time
- Z-score
- Trade signals
- Equity curve

---

## Step 7: Extensions (Optional)

Once base model works:

### Add funding rates
- Improve signal quality

### Try different windows
- 10, 20, 50 periods

### Add volatility filter
- Trade only in certain regimes

### Multi-asset
- ETH, SOL, etc.

---

## Key Challenges

- Aligning spot and futures timestamps
- Handling missing data
- Avoiding lookahead bias
- Properly modelling PnL

---

## What This Project Demonstrates

- Data engineering skills
- Quantitative signal construction
- Backtesting discipline
- Understanding of relative value trading

---

## Notes

- No API key required
- Respect API rate limits
- Cache data locally for efficiency

---

## Next Steps

- Convert into modular pipeline:
  - `/data`
  - `/signals`
  - `/backtest`

- Add dashboard (Streamlit)

- Expand to multi-asset strategies
