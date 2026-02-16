"""Tests for the citation enrichment module."""

from __future__ import annotations

import pytest

from rlm_legal_docs.citations import CitationEnricher
from rlm_legal_docs.extraction import ExtractionResult


@pytest.fixture
def extraction_results():
    return [
        ExtractionResult(
            doc_name="contract.pdf",
            extractions=[
                {
                    "extraction_class": "party",
                    "extraction_text": "Acme Corporation",
                    "char_start": 142,
                    "char_end": 158,
                    "attributes": {"role": "buyer"},
                },
                {
                    "extraction_class": "date",
                    "extraction_text": "January 15, 2024",
                    "char_start": 312,
                    "char_end": 328,
                    "attributes": {},
                },
            ],
        ),
        ExtractionResult(
            doc_name="letter.pdf",
            extractions=[
                {
                    "extraction_class": "monetary_amount",
                    "extraction_text": "USD 2,500,000",
                    "char_start": 50,
                    "char_end": 63,
                    "attributes": {},
                },
            ],
        ),
    ]


@pytest.fixture
def enricher(extraction_results):
    return CitationEnricher(extraction_results)


class TestCitationEnricher:
    def test_parse_verified_citation(self, enricher):
        text = "The buyer is Acme Corporation [Source: contract.pdf, chars 142-158]."
        result = enricher.enrich(text)
        assert len(result.citations) == 1
        assert result.citations[0].doc_name == "contract.pdf"
        assert result.citations[0].char_start == 142
        assert result.citations[0].char_end == 158
        assert result.citations[0].verified is True
        assert result.citations[0].extraction_text == "Acme Corporation"

    def test_parse_unverified_citation(self, enricher):
        text = "Some claim [Source: unknown.pdf, chars 0-10]."
        result = enricher.enrich(text)
        assert len(result.citations) == 1
        assert result.citations[0].verified is False
        assert result.citations[0].extraction_text == ""

    def test_multiple_citations(self, enricher):
        text = (
            "The agreement dated [Source: contract.pdf, chars 312-328] "
            "involves [Source: contract.pdf, chars 142-158] "
            "for [Source: letter.pdf, chars 50-63]."
        )
        result = enricher.enrich(text)
        assert len(result.citations) == 3

    def test_no_citations(self, enricher):
        text = "This text has no citations at all."
        result = enricher.enrich(text)
        assert len(result.citations) == 0
        assert result.has_analysis_markers is False

    def test_analysis_marker_detected(self, enricher):
        text = "[Analysis] Based on the above, the risk is moderate."
        result = enricher.enrich(text)
        assert result.has_analysis_markers is True

    def test_analysis_marker_not_present(self, enricher):
        text = "Just a regular statement."
        result = enricher.enrich(text)
        assert result.has_analysis_markers is False

    def test_empty_response(self, enricher):
        result = enricher.enrich("")
        assert len(result.citations) == 0
        assert result.text == ""

    def test_citation_with_char_singular(self, enricher):
        """Test that 'char' (singular) also works in the pattern."""
        text = "Claim [Source: contract.pdf, char 142-158]."
        result = enricher.enrich(text)
        assert len(result.citations) == 1
        assert result.citations[0].verified is True

    def test_enriched_response_preserves_text(self, enricher):
        text = "Original text [Source: contract.pdf, chars 142-158]."
        result = enricher.enrich(text)
        assert result.text == text
