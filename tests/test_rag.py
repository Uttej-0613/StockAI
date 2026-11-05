from types import SimpleNamespace
import pytest
from backend.services import rag


def test_chunk_returns_overlapping_segments():
    words = [f"word{i}" for i in range(2500)]
    chunks = rag._chunk(" ".join(words), size=1000, overlap=100)
    assert len(chunks) >= 3
    assert "word999" in chunks[0]
    assert "word900" in chunks[1]


def test_chunk_handles_empty_and_whitespace():
    assert rag._chunk("  \n \t ") == []
    assert rag._chunk("alpha   beta") == ["alpha beta"]


def test_lexical_score_prefers_matching_passage():
    relevant = rag._lexical_score("quarterly revenue growth", "Quarterly revenue growth accelerated")
    unrelated = rag._lexical_score("quarterly revenue growth", "Weather and climate patterns")
    assert relevant > unrelated


def test_extract_text_supports_utf8_text():
    assert rag._extract_text("report.txt", b"Revenue increased") == "Revenue increased"


def test_extract_text_rejects_unknown_extension():
    with pytest.raises(ValueError, match="Supported formats"):
        rag._extract_text("report.exe", b"payload")


def test_ingest_uses_lexical_fallback_without_api_key(monkeypatch):
    saved = {}
    monkeypatch.setattr(rag, "get_settings", lambda: SimpleNamespace(openai_api_key=None))
    monkeypatch.setattr(rag, "save_document", lambda filename, digest, chunks: saved.update(filename=filename, digest=digest, chunks=chunks) or 7)
    result = rag.ingest("notes.txt", b"Quarterly revenue increased by twelve percent.")
    assert result["document_id"] == 7
    assert result["embedding"] == "lexical_fallback"
    assert saved["chunks"][0]["embedding"] is None


def test_retrieve_returns_relevant_chunks(monkeypatch):
    rows = [
        {"id": 1, "filename": "annual.txt", "document_id": 1, "chunk_index": 0, "content": "Revenue and profit increased in the quarter", "embedding": None},
        {"id": 2, "filename": "weather.txt", "document_id": 2, "chunk_index": 0, "content": "Rainfall and temperature forecast", "embedding": None},
    ]
    monkeypatch.setattr(rag, "get_chunks", lambda: rows)
    monkeypatch.setattr(rag, "get_settings", lambda: SimpleNamespace(openai_api_key=None))
    results = rag.retrieve("quarter revenue", top_k=1)
    assert len(results) == 1
    assert results[0]["source"] == "annual.txt"
