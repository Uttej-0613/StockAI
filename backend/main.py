from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from live_data import get_live_stock
from ml_model import predict_trend
from rag_engine import answer_query
from news_sentiment import get_stock_news

app = FastAPI(title="Stock AI Assistant")

portfolio = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message":"Stock AI Running"}

@app.get("/stock/{symbol}")
def stock(symbol:str):

    data = get_live_stock(symbol)

    if not data:
        return {"error":"Stock not found"}

    prediction = predict_trend(data)

    news = get_stock_news(symbol)

    return {

        "symbol":data["symbol"],
        "company":data["company"],
        "sector":data["sector"],
        "pe_ratio":data["pe_ratio"],

        "open":data["open"],
        "close":data["close"],
        "volume":data["volume"],

        "moving_average":data["moving_average"],
        "rsi":data["rsi"],

        "trend":prediction["trend"],
        "advice":prediction["advice"],
        "score":prediction["score"],

        "prices":data["prices"],
        "dates":data["dates"],

        "news":news
    }

@app.get("/ask/{symbol}/{question}")
def ask(symbol:str,question:str):

    data = get_live_stock(symbol)

    if not data:
        return {"answer":"Stock not found"}

    answer = answer_query(symbol,question,data)

    return {"answer":answer}

@app.get("/top-stocks")
def top_stocks():

    stocks = [
        "NVDA","AAPL","MSFT","AMZN","GOOGL",
        "TSLA","META","AMD","NFLX","INTC"
    ]

    return {"stocks":stocks}

@app.post("/portfolio/add/{symbol}/{qty}")
def add_portfolio(symbol:str,qty:int):

    portfolio.append({"symbol":symbol,"quantity":qty})

    return {"portfolio":portfolio}

@app.get("/portfolio")
def view_portfolio():

    return {"portfolio":portfolio}