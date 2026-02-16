"""Integration tests for the full extraction pipeline.

These tests require a LANGEXTRACT_API_KEY to run and are skipped in CI
unless the key is provided.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
HAS_API_KEY = bool(os.getenv("LANGEXTRACT_API_KEY"))


@pytest.mark.skipif(not HAS_API_KEY, reason="LANGEXTRACT_API_KEY not set")
class TestFullPipeline:
    """End-to-end tests that hit the LangExtract API."""

    def test_extract_and_build_context(self):
        from rlm_legal_docs.extraction import (
            build_enriched_context,
            run_batch_extraction,
        )
        from rlm_legal_docs.query import build_structured_context

        # Load sample docs
        contract = (FIXTURES_DIR / "sample_contract.txt").read_text(encoding="utf-8")
        correspondence = (FIXTURES_DIR / "sample_correspondence.txt").read_text(encoding="utf-8")

        docs = [
            {"name": "sample_contract.txt", "text": contract},
            {"name": "sample_correspondence.txt", "text": correspondence},
        ]

        # Run extraction
        results, annotated = run_batch_extraction(
            docs,
            schema_name="general",
            extraction_passes=1,  # Faster for testing
            max_workers=2,
        )

        assert len(results) == 2
        # At least some extractions should be found
        total = sum(len(r.extractions) for r in results if not r.error)
        assert total > 0

        # Build enriched context
        raw_context = build_structured_context(docs)
        enriched = build_enriched_context(results, raw_context)

        assert "===== EXTRACTION INDEX =====" in enriched
        assert "===== DOCUMENT 1:" in enriched
        assert "===== DOCUMENT 2:" in enriched


class TestPipelineWithMocks:
    """Tests that verify pipeline wiring without API calls."""

    def test_enriched_context_contains_both_sections(self):
        from rlm_legal_docs.extraction import (
            ExtractionResult,
            build_enriched_context,
        )
        from rlm_legal_docs.query import build_structured_context

        docs = [{"name": "test.txt", "text": "Hello world"}]
        raw = build_structured_context(docs)

        results = [
            ExtractionResult(
                doc_name="test.txt",
                extractions=[
                    {
                        "extraction_class": "party",
                        "extraction_text": "Hello",
                        "char_start": 0,
                        "char_end": 5,
                        "attributes": {},
                    }
                ],
            )
        ]

        enriched = build_enriched_context(results, raw)
        assert "EXTRACTION INDEX" in enriched
        assert "Hello world" in enriched

    def test_extraction_results_with_errors_still_produce_context(self):
        from rlm_legal_docs.extraction import (
            ExtractionResult,
            build_enriched_context,
        )
        from rlm_legal_docs.query import build_structured_context

        docs = [{"name": "test.txt", "text": "Some text"}]
        raw = build_structured_context(docs)

        results = [
            ExtractionResult(doc_name="test.txt", error="API failed")
        ]

        enriched = build_enriched_context(results, raw)
        assert "extraction failed" in enriched
        assert "Some text" in enriched
