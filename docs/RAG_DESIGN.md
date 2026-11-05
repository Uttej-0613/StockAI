# RAG design and operating notes

1. **Ingestion:** validate extension and upload size; extract text (PDF extraction is optional via pypdf); normalize whitespace.
2. **Chunking:** word-window chunks with overlap preserve local context and avoid whole-report prompts.
3. **Embedding:** OpenAI `text-embedding-3-small` embeddings are batched and persisted in SQLite. This keeps the default install small; embeddings are API-backed, not a local model.
4. **Retrieval:** cosine similarity ranks embedded chunks. If there is no key or no embeddings, a lexical ranker is used and surfaced as a degraded mode. It is not described as semantic retrieval.
5. **Generation:** retrieved excerpts and a separate market snapshot are sent to the configured chat model. The system prompt treats documents as untrusted data, requires citations, and prohibits unsupported financial advice.
6. **Evaluation:** add a labelled question/answer set from real filings; measure Recall@k, MRR, citation precision, answer faithfulness, and no-answer behaviour before claiming production quality.

## Known next steps

- Move to PostgreSQL + pgvector for multi-user scale and transactional vector search.
- Add document page-level metadata and page citations (current citations identify filename and chunk).
- Add ingestion job queue, retries, rate limits, request authentication, observability, and tenant isolation before public deployment.
