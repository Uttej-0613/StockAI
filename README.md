# StockAI — Financial Research, Grounded by Evidence

StockAI is a lightweight financial research workspace combining market data, document-grounded retrieval-augmented generation (RAG), and a responsive dashboard. It is an educational research tool, **not investment advice**.

## What it does

- Fetches historical market data and computes transparent indicators (SMA, EMA, RSI, daily change).
- Ingests PDF, Markdown, text, and CSV research documents into a persistent SQLite knowledge store.
- Chunks documents with overlap, embeds them with OpenAI embeddings when configured, and retrieves relevant passages using cosine similarity. If embeddings are unavailable, retrieval degrades explicitly to lexical ranking rather than pretending semantic search happened.
- Answers questions from retrieved evidence with source citations. Market data is passed as a separate, timestamped context.
- Stores a local watchlist and ingested document metadata.
- Exposes a versioned FastAPI API and a polished browser dashboard.

## Architecture

```text
frontend/index.html
       │ HTTP /api/v1
backend/main.py ── services/market.py
       │           services/rag.py ── SQLite (chunks + embeddings)
       └────────── services/storage.py
```

The RAG pipeline is deliberately explicit: extract → normalize → chunk → embed → persist → retrieve → answer with citations. No hidden if/else chatbot is presented as RAG.

## Quick start (Python 3.11+)

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows; on macOS/Linux use: cp .env.example .env
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs.

Add an OpenAI API key to `.env` to enable generated answers and semantic embeddings. Without a key, StockAI still provides market data and evidence retrieval, but returns retrieved evidence instead of fabricating an LLM answer. API usage incurs provider costs.

## Document ingestion

```bash
curl -X POST http://127.0.0.1:8000/api/v1/documents/ingest \
  -F "file=@your_quarterly_report.pdf"
```

Supported formats: PDF (requires `pypdf`), TXT, Markdown, and CSV. Install `pypdf` for PDF support: `pip install pypdf`.

Ask a question:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What were the main revenue risks?","symbol":"TCS.NS"}'
```

## Configuration

See `.env.example`. SQLite is used by default; set `DATABASE_PATH` to persist data elsewhere. Never commit `.env`, API keys, user documents, or database files.

## Quality and limitations

- Market data availability, delays, symbol coverage, and terms depend on Yahoo Finance/yfinance.
- The application does not guarantee data accuracy or real-time execution prices.
- RAG answer quality depends on document quality, chunk coverage, embedding availability, and the LLM. Inspect citations before relying on an answer.
- No fabricated price forecasts or buy/sell recommendations are produced.
- Run tests with `pytest`.

## License

MIT.

## Deployment security boundary

For a protected API deployment, set `ENVIRONMENT=production` and configure a strong `STOCKAI_API_KEY`. Protected API routes require the `X-API-Key` header; liveness and readiness endpoints remain public. Do not embed this shared key in browser JavaScript. Put the dashboard and API behind a trusted identity-aware reverse proxy, terminate TLS there, and add rate limiting and request quotas.

The API-key option is a single shared credential, not user authentication or tenant isolation. The default SQLite database is suitable for a single-instance portfolio deployment, not a horizontally scaled multi-user service. Before public multi-user use, add per-user authorization, tenant-scoped document access, managed database/storage with backups, secret management, monitoring/alerts, and a tested deployment/rollback process. Market data is supplied by yfinance and has no availability or freshness SLA. Validate all financial answers against a labelled evaluation set before relying on them.
