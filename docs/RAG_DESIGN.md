# RAG design and evaluation

## Retrieval pipeline

1. **Ingestion:** validate extension and upload size; extract PDF text with pypdf or decode TXT, Markdown, and CSV.
2. **Chunking:** normalize whitespace and split into overlapping word windows so context is preserved across boundaries.
3. **Embedding:** batch chunks through OpenAI text-embedding-3-small and persist vectors with document metadata in SQLite.
4. **Hybrid retrieval:** rank all chunks lexically and rank embedded chunks by cosine similarity. Combine the independent rankings with Reciprocal Rank Fusion (RRF), avoiding direct addition of incomparable raw scores. If embeddings are unavailable, lexical retrieval remains explicit.
5. **Generation:** pass retrieved evidence and a separate market snapshot to the configured chat model. The prompt treats retrieved text as untrusted, requires citations, and prohibits unsupported financial advice.

## Evaluation before production claims

Build a labelled query set from real annual reports and quarterly filings. Measure:
- Recall@k and MRR for retrieval quality.
- Citation precision: whether each cited passage supports the associated claim.
- Faithfulness: whether answers contain claims absent from retrieved evidence.
- No-answer accuracy for questions not covered by the corpus.
- Latency and token cost per ingestion and query.

## Scaling and known limitations

SQLite JSON vectors are appropriate for a small local portfolio demo, not large corpora. For multi-user production, move metadata to PostgreSQL and vectors to pgvector, add document page/section metadata, background ingestion jobs, retries, authentication, rate limits, tenant isolation, and observability. Current citations identify file and chunk, not exact PDF page. An API key and provider billing are required for semantic embeddings and generated answers.
