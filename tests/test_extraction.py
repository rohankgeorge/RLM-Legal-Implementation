"""Tests for the extraction engine module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from rlm_legal_docs.extraction import (
    ExtractionResult,
    build_enriched_context,
    format_extraction_index,
    run_extraction,
)

# ---------------------------------------------------------------------------
# format_extraction_index
# ---------------------------------------------------------------------------


class TestFormatExtractionIndex:
    def test_with_extractions(self):
        results = [
            ExtractionResult(
                doc_name="contract.pdf",
                extractions=[
                    {
                        "extraction_class": "party",
                        "extraction_text": "Acme Corp",
                        "char_start": 10,
                        "char_end": 19,
                        "attributes": {"role": "buyer"},
                    },
                    {
                        "extraction_class": "date",
                        "extraction_text": "January 1, 2024",
                        "char_start": 50,
                        "char_end": 65,
                        "attributes": {},
                    },
                ],
            )
        ]
        output = format_extraction_index(results)
        assert "===== EXTRACTION INDEX =====" in output
        assert "[Document: contract.pdf]" in output
        assert 'party: "Acme Corp" (chars 10-19)' in output
        assert "{'role': 'buyer'}" in output
        assert 'date: "January 1, 2024" (chars 50-65)' in output

    def test_with_error(self):
        results = [
            ExtractionResult(doc_name="bad.pdf", error="API timeout")
        ]
        output = format_extraction_index(results)
        assert "(extraction failed: API timeout)" in output

    def test_with_no_extractions(self):
        results = [
            ExtractionResult(doc_name="empty.pdf", extractions=[])
        ]
        output = format_extraction_index(results)
        assert "(no extractions found)" in output

    def test_empty_results(self):
        output = format_extraction_index([])
        assert "===== EXTRACTION INDEX =====" in output

    def test_multiple_documents(self):
        results = [
            ExtractionResult(
                doc_name="doc1.pdf",
                extractions=[
                    {
                        "extraction_class": "party",
                        "extraction_text": "Alice",
                        "char_start": 0,
                        "char_end": 5,
                        "attributes": {},
                    }
                ],
            ),
            ExtractionResult(
                doc_name="doc2.pdf",
                extractions=[
                    {
                        "extraction_class": "date",
                        "extraction_text": "2024-01-01",
                        "char_start": 10,
                        "char_end": 20,
                        "attributes": {},
                    }
                ],
            ),
        ]
        output = format_extraction_index(results)
        assert "[Document: doc1.pdf]" in output
        assert "[Document: doc2.pdf]" in output


# ---------------------------------------------------------------------------
# build_enriched_context
# ---------------------------------------------------------------------------


class TestBuildEnrichedContext:
    def test_combines_index_and_raw(self):
        results = [
            ExtractionResult(
                doc_name="test.pdf",
                extractions=[
                    {
                        "extraction_class": "party",
                        "extraction_text": "TestCo",
                        "char_start": 0,
                        "char_end": 6,
                        "attributes": {},
                    }
                ],
            )
        ]
        raw_context = "===== DOCUMENT 1: test.pdf =====\n\nSome raw text here."
        output = build_enriched_context(results, raw_context)
        assert "===== EXTRACTION INDEX =====" in output
        assert "===== DOCUMENT 1: test.pdf =====" in output
        assert "Some raw text here." in output
        # Index comes before raw context
        idx_pos = output.index("EXTRACTION INDEX")
        doc_pos = output.index("DOCUMENT 1")
        assert idx_pos < doc_pos


# ---------------------------------------------------------------------------
# run_extraction (mocked)
# ---------------------------------------------------------------------------


class TestRunExtraction:
    @patch("rlm_legal_docs.extraction.lx")
    @patch("rlm_legal_docs.extraction.get_schema")
    def test_success(self, mock_get_schema, mock_lx):
        mock_get_schema.return_value = {
            "prompt_description": "Extract entities",
            "examples": [],
        }

        # Mock annotated document
        mock_ext = MagicMock()
        mock_ext.extraction_class = "party"
        mock_ext.extraction_text = "Acme Corp"
        mock_ext.char_interval = (10, 19)
        mock_ext.attributes = {"role": "buyer"}

        mock_doc = MagicMock()
        mock_doc.extractions = [mock_ext]
        mock_lx.extract.return_value = [mock_doc]

        result, annotated = run_extraction(
            text="Some legal text with Acme Corp",
            doc_name="test.pdf",
        )

        assert result.doc_name == "test.pdf"
        assert result.error is None
        assert len(result.extractions) == 1
        assert result.extractions[0]["extraction_class"] == "party"
        assert result.extractions[0]["extraction_text"] == "Acme Corp"
        assert result.extractions[0]["char_start"] == 10
        assert result.extractions[0]["char_end"] == 19
        assert annotated is not None

    @patch("rlm_legal_docs.extraction.lx")
    @patch("rlm_legal_docs.extraction.get_schema")
    def test_api_failure(self, mock_get_schema, mock_lx):
        mock_get_schema.return_value = {
            "prompt_description": "Extract entities",
            "examples": [],
        }
        mock_lx.extract.side_effect = RuntimeError("API connection failed")

        result, annotated = run_extraction(
            text="Some text",
            doc_name="test.pdf",
        )

        assert result.doc_name == "test.pdf"
        assert result.error is not None
        assert "API connection failed" in result.error
        assert result.extractions == []
        assert annotated is None
