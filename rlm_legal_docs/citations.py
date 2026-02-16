"""Post-processing citation enrichment for RLM responses.

Parses inline [Source: ...] citation markers, validates them against
the extraction index, and detects [Analysis] markers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Citation:
    """A single source citation extracted from an RLM response."""

    doc_name: str
    char_start: int
    char_end: int
    extraction_text: str = ""
    verified: bool = False


@dataclass
class EnrichedResponse:
    """RLM response enriched with parsed citation metadata."""

    text: str
    citations: list[Citation] = field(default_factory=list)
    has_analysis_markers: bool = False


# Pattern: [Source: filename.pdf, chars 142-171]
_CITATION_RE = re.compile(
    r"\[Source:\s*([^,\]]+),\s*chars?\s*(\d+)\s*-\s*(\d+)\s*\]"
)
_ANALYSIS_RE = re.compile(r"\[Analysis\]")


class CitationEnricher:
    """Enriches RLM responses with verified citation metadata.

    Uses exact matching against the extraction index to verify citations.
    Conservative by design: no fuzzy matching in v1.
    """

    def __init__(self, extraction_results: list):
        """Build lookup index from extraction results.

        Args:
            extraction_results: List of ExtractionResult objects from ingestion.
        """
        self._index: dict[tuple[str, int, int], str] = {}
        for r in extraction_results:
            if hasattr(r, "extractions"):
                for ext in r.extractions:
                    key = (r.doc_name, ext["char_start"], ext["char_end"])
                    self._index[key] = ext["extraction_text"]

    def enrich(self, response_text: str) -> EnrichedResponse:
        """Parse and validate citations in the RLM response.

        Args:
            response_text: Raw text response from the RLM.

        Returns:
            EnrichedResponse with parsed citations and analysis marker detection.
        """
        citations: list[Citation] = []
        for m in _CITATION_RE.finditer(response_text):
            doc_name = m.group(1).strip()
            char_start = int(m.group(2))
            char_end = int(m.group(3))
            key = (doc_name, char_start, char_end)
            verified = key in self._index
            citations.append(
                Citation(
                    doc_name=doc_name,
                    char_start=char_start,
                    char_end=char_end,
                    extraction_text=self._index.get(key, ""),
                    verified=verified,
                )
            )

        has_analysis = bool(_ANALYSIS_RE.search(response_text))

        return EnrichedResponse(
            text=response_text,
            citations=citations,
            has_analysis_markers=has_analysis,
        )
