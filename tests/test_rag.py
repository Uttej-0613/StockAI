from backend.services.rag import _chunk, _lexical_score

def test_chunk_returns_overlapping_segments():
    words = [f"word{i}" for i in range(2500)]
    chunks = _chunk(" ".join(words), size=1000, overlap=100)
    assert len(chunks) >= 3
    assert "word999" in chunks[0]
    assert "word900" in chunks[1]

def test_lexical_score_prefers_matching_passage():
    relevant = _lexical_score("quarterly revenue growth", "Quarterly revenue growth accelerated")
    unrelated = _lexical_score("quarterly revenue growth", "Weather and climate patterns")
    assert relevant > unrelated
