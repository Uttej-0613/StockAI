import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_stock_news(symbol):

    try:

        symbol = symbol.upper()

        stock = yf.Ticker(symbol)

        news = stock.news

        results = []

        if not news:
            return []

        for item in news[:5]:

            title = item.get("title","")

            score = analyzer.polarity_scores(title)["compound"]

            # improved thresholds
            if score >= 0.05:
                sentiment = "Positive 📈"

            elif score <= -0.05:
                sentiment = "Negative 📉"

            else:
                sentiment = "Neutral ⚖️"

            results.append({
                "title": title,
                "sentiment": sentiment
            })

        return results

    except Exception as e:

        print("News error:", e)

        return []