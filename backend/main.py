from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.config import get_settings
from backend.schemas import ChatRequest, WatchlistRequest
from backend.services import storage
from backend.services.market import get_market_snapshot
from backend.services.rag import answer, ingest

@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.initialize()
    yield

app = FastAPI(title="StockAI API", version="2.0.0", description="Evidence-grounded financial research assistant", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET","POST","DELETE"], allow_headers=["Content-Type"])

@app.get("/api/v1/health")
def health():
    return {"status":"ok","service":"StockAI","version":"2.0.0"}

@app.get("/api/v1/market/{symbol}")
def market(symbol: str):
    try:
        return get_market_snapshot(symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except LookupError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        raise HTTPException(502, f"Market data provider failed: {type(exc).__name__}")

@app.post("/api/v1/chat")
def chat(request: ChatRequest):
    snapshot = None
    if request.symbol:
        try:
            snapshot = get_market_snapshot(request.symbol)
        except Exception:
            snapshot = None
    try:
        return answer(request.question, request.symbol, snapshot, request.top_k)
    except Exception as exc:
        raise HTTPException(502, f"AI provider failed: {type(exc).__name__}")

@app.post("/api/v1/documents/ingest")
async def ingest_document(file: UploadFile = File(...)):
    payload = await file.read()
    if len(payload) > 15 * 1024 * 1024:
        raise HTTPException(413, "Maximum upload size is 15 MB.")
    try:
        return ingest(Path(file.filename or "document.txt").name, payload)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(502, f"Document ingestion failed: {type(exc).__name__}")

@app.get("/api/v1/documents")
def documents():
    return {"documents":storage.list_documents()}

@app.get("/api/v1/watchlist")
def watchlist():
    return {"symbols":storage.get_watchlist()}

@app.post("/api/v1/watchlist")
def add_watchlist(request: WatchlistRequest):
    storage.add_watchlist(request.symbol)
    return watchlist()

@app.delete("/api/v1/watchlist/{symbol}")
def delete_watchlist(symbol: str):
    storage.remove_watchlist(symbol)
    return watchlist()

@app.get("/")
def dashboard():
    return FileResponse(Path(__file__).resolve().parent.parent / "frontend" / "index.html")
