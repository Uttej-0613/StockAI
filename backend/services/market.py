from datetime import datetime, timezone
import pandas as pd
import yfinance as yf

def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))

def get_market_snapshot(symbol: str, period: str = "6mo") -> dict:
    clean = symbol.strip().upper()
    if not clean or len(clean) > 24 or any(ch.isspace() for ch in clean):
        raise ValueError("Enter a valid ticker symbol.")
    candidates = [clean]
    if "." not in clean and not clean.endswith("-USD"):
        candidates.append(f"{clean}.NS")
    frame = pd.DataFrame()
    resolved = clean
    for candidate in candidates:
        try:
            frame = yf.Ticker(candidate).history(period=period, auto_adjust=True)
            if not frame.empty:
                resolved = candidate
                break
        except Exception:
            continue
    if frame.empty:
        raise LookupError(f"No market history found for {clean}. Check the ticker and try again.")
    close = frame["Close"].dropna()
    latest = frame.iloc[-1]
    previous = frame.iloc[-2] if len(frame) > 1 else latest
    price = float(latest["Close"])
    prior = float(previous["Close"])
    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    rsi_value = _rsi(close).iloc[-1]
    info = {}
    try:
        info = yf.Ticker(resolved).get_info() or {}
    except Exception:
        pass
    return {
        "symbol": resolved, "company": info.get("longName") or info.get("shortName") or resolved,
        "currency": info.get("currency") or ("INR" if resolved.endswith(".NS") else "USD"),
        "price": round(price, 4), "previous_close": round(prior, 4),
        "change": round(price-prior, 4), "change_percent": round(((price-prior)/prior)*100, 3) if prior else None,
        "volume": int(latest.get("Volume", 0) or 0), "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"), "sector": info.get("sector"),
        "sma20": round(sma20, 4) if sma20 is not None and pd.notna(sma20) else None,
        "sma50": round(sma50, 4) if sma50 is not None and pd.notna(sma50) else None,
        "rsi14": round(float(rsi_value), 2) if pd.notna(rsi_value) else None,
        "history": [{"date": idx.strftime("%Y-%m-%d"), "close": round(float(value),4)} for idx,value in close.tail(120).items()],
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance via yfinance"
    }
