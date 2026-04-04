def predict_trend(data):

    price = data["close"]
    ma = data["moving_average"]
    rsi = data["rsi"]

    score = 50

    if price > ma:
        trend = "Bullish 📈"
        score += 20
    else:
        trend = "Bearish 📉"
        score -= 10

    if rsi < 70:
        score += 10

    if rsi > 70:
        advice = "SELL"
    elif price > ma:
        advice = "BUY"
    else:
        advice = "HOLD"

    return {

        "trend": trend,

        "advice": advice,

        "score": score
    }