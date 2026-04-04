import yfinance as yf
import pandas as pd

def calculate_rsi(data, window=14):

    delta = data.diff()

    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_live_stock(symbol):

    symbol = symbol.upper()

    stock = yf.Ticker(symbol)

    data = stock.history(period="1mo")

    if data.empty:
        symbol = symbol + ".NS"
        stock = yf.Ticker(symbol)
        data = stock.history(period="1mo")

    if data.empty:
        return None

    latest = data.iloc[-1]

    prices = data["Close"].tolist()
    dates = data.index.strftime("%Y-%m-%d").tolist()

    moving_avg = data["Close"].rolling(20).mean().iloc[-1]

    rsi = calculate_rsi(data["Close"]).iloc[-1]

    info = stock.info

    return {

        "symbol": symbol,

        "company": info.get("longName","Unknown"),

        "sector": info.get("sector","Unknown"),

        "pe_ratio": info.get("trailingPE",0),

        "open": float(latest["Open"]),

        "close": float(latest["Close"]),

        "volume": int(latest["Volume"]),

        "moving_average": float(moving_avg) if pd.notna(moving_avg) else 0,

        "rsi": float(rsi) if pd.notna(rsi) else 0,

        "prices": prices,

        "dates": dates
    }