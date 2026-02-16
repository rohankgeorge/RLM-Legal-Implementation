"""Tests for the extraction store (cache layer)."""

from __future__ import annotations

import pytest

from rlm_legal_docs.extraction import ExtractionResult
from rlm_legal_docs.extraction_store import ExtractionStore


@pytest.fixture
def store(tmp_path):
    """Create an ExtractionStore using a temporary directory."""
    return ExtractionStore(cache_dir=str(tmp_path / "cache"))


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file for cache key computation."""
    f = tmp_path / "sample.txt"
    f.write_text("Hello world")
    return f


@pytest.fixture
def sample_result():
    return ExtractionResult(
        doc_name="sample.txt",
        extractions=[
            {
                "extraction_class": "party",
                "extraction_text": "Acme",
                "char_start": 0,
                "char_end": 4,
                "attributes": {},
            }
        ],
    )


class TestExtractionStore:
    def test_cache_miss(self, store, sample_file):
        result = store.get(str(sample_file), "general")
        assert result is None

    def test_put_then_get(self, store, sample_file, sample_result):
        store.put(str(sample_file), "general", sample_result)
        cached = store.get(str(sample_file), "general")

        assert cached is not None
        assert cached.doc_name == "sample.txt"
        assert len(cached.extractions) == 1
        assert cached.extractions[0]["extraction_class"] == "party"

    def test_different_schema_is_separate(self, store, sample_file, sample_result):
        store.put(str(sample_file), "general", sample_result)

        # Different schema should miss
        cached = store.get(str(sample_file), "contract")
        assert cached is None

    def test_mtime_change_invalidates(self, store, sample_file, sample_result):
        store.put(str(sample_file), "general", sample_result)

        # Modify file (changes mtime)
        sample_file.write_text("Modified content")

        cached = store.get(str(sample_file), "general")
        assert cached is None

    def test_clear(self, store, sample_file, sample_result):
        store.put(str(sample_file), "general", sample_result)
        store.clear()
        cached = store.get(str(sample_file), "general")
        assert cached is None

    def test_error_result_round_trip(self, store, sample_file):
        error_result = ExtractionResult(
            doc_name="bad.pdf",
            error="API failed",
        )
        store.put(str(sample_file), "general", error_result)
        cached = store.get(str(sample_file), "general")
        assert cached is not None
        assert cached.error == "API failed"
        assert cached.extractions == []
