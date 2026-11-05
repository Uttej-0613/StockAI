from contextlib import asynccontextmanager
from pathlib import Path
import hmac
import logging
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from backend.config import get_settings
from backend.schemas import ChatRequest, WatchlistRequest
from backend.services import storage
from backend.services.market import get_market_snapshot
from backend.services.rag import answer, ingest

logger = logging.getLogger("stockai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.initialize()
    yield

app = FastAPI(title="StockAI API", version="2.1.0", description="Evidence-grounded financial research assistant", lifespan=lifespan)
settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False, allow_methods=["GET","POST","DELETE"], allow_headers=["Content-Type", "X-API-Key"])

@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    current = get_settings()
    if current.environment == "production" and not current.api_key:
        return JSONResponse(status_code=503, content={"detail": "Service authentication is not configured."})
    if current.api_key and request.url.path not in {"/api/v1/health", "/api/v1/ready"}:
        supplied = request.headers.get("X-API-Key", "")
        if not hmac.compare_digest(supplied, current.api_key):
            return JSONResponse(status_code=401, content={"detail": "A valid API key is required."})
    return await call_next(request)

@app.get("/api/v1/health")
def health():
    return {"status":"ok","service":"StockAI","version":"2.1.0"}

@app.get("/api/v1/ready")
def ready():
    try:
        with storage.connect() as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(503, "Database is not ready.") from exc

@app.get("/api/v1/market/{symbol}")
def market(symbol: str):
    try:
        return get_market_snapshot(symbol)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except LookupError as exc:
        raise HTTPException(404, str(exc))
    except Exception as exc:
        logger.exception("Market data provider failed")
        raise HTTPException(502, "Market data provider is temporarily unavailable.") from exc

@app.post("/api/v1/chat")
def chat(request: ChatRequest):
    snapshot = None
    if request.symbol:
        try:
            snapshot = get_market_snapshot(request.symbol)
        except Exception:
            logger.warning("Market snapshot unavailable for chat request", exc_info=True)
    try:
        return answer(request.question, request.symbol, snapshot, request.top_k)
    except Exception as exc:
        logger.exception("AI request failed")
        raise HTTPException(502, "AI provider is temporarily unavailable.") from exc

@app.post("/api/v1/documents/ingest")
async def ingest_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "document.txt").name
    limit = get_settings().max_upload_bytes
    payload = await file.read(limit + 1)
    if len(payload) > limit:
        raise HTTPException(413, "Maximum upload size exceeded.")
    try:
        return ingest(filename, payload)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        logger.exception("Document ingestion failed")
        raise HTTPException(502, "Document ingestion failed. Check provider configuration and retry.") from exc

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
