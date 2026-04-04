def answer_query(symbol, question, data):

    question = question.lower()

    price = data["close"]
    volume = data["volume"]
    rsi = data["rsi"]
    ma = data["moving_average"]

    if "price" in question:
        return f"The current price of {symbol} is {price}"

    if "volume" in question:
        return f"The trading volume today is {volume}"

    if "rsi" in question:
        return f"The RSI indicator is {rsi}. Values above 70 indicate overbought."

    if "trend" in question:
        if price > ma:
            return "The stock is currently bullish."
        else:
            return "The stock is currently bearish."

    if "long term" in question or "invest" in question:
        if price > ma and rsi < 70:
            return "The stock looks healthy for long-term investment."
        else:
            return "The stock might need more analysis before long-term investment."

    return "Ask about price, trend, RSI, volume or investment advice."