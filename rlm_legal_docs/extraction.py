"""LangExtract wrapper for legal document extraction.

Provides functions to run structured extraction on documents,
format results as a plain-text index, and build enriched context
for the RLM.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import langextract as lx

from rlm_legal_docs.extraction_schemas import get_schema

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of extracting entities from a single document."""

    doc_name: str
    extractions: list[dict] = field(default_factory=list)
    error: str | None = None


def run_extraction(
    text: str,
    doc_name: str,
    schema_name: str = "general",
    model_id: str = "gemini-2.5-flash",
    api_key: str | None = None,
    max_char_buffer: int = 2000,
    extraction_passes: int = 2,
    max_workers: int = 5,
) -> tuple[ExtractionResult, list | None]:
    """Run LangExtract on a single document.

    Returns a tuple of (ExtractionResult, raw_annotated_docs).
    The raw_annotated_docs are needed for visualization but should
    not be serialized to cache.

    Never raises — errors are captured in ExtractionResult.error.
    """
    try:
        schema = get_schema(schema_name)
        kwargs: dict = {
            "text_or_documents": text,
            "prompt_description": schema["prompt_description"],
            "examples": schema["examples"],
            "model_id": model_id,
            "max_char_buffer": max_char_buffer,
            "extraction_passes": extraction_passes,
            "max_workers": max_workers,
        }
        if api_key:
            kwargs["api_key"] = api_key

        annotated_docs = lx.extract(**kwargs)

        extractions: list[dict] = []
        for doc in annotated_docs:
            for ext in doc.extractions:
                extractions.append(
                    {
                        "extraction_class": ext.extraction_class,
                        "extraction_text": ext.extraction_text,
                        "char_start": ext.char_interval[0],
                        "char_end": ext.char_interval[1],
                        "attributes": ext.attributes or {},
                    }
                )

        return ExtractionResult(doc_name=doc_name, extractions=extractions), annotated_docs

    except Exception as e:
        logger.warning("Extraction failed for %s: %s", doc_name, e)
        return ExtractionResult(doc_name=doc_name, error=str(e)), None


def run_batch_extraction(
    docs: list[dict[str, str]],
    schema_name: str = "general",
    **kwargs,
) -> tuple[list[ExtractionResult], list]:
    """Run extraction on multiple documents sequentially.

    Returns (list of ExtractionResult, list of all raw annotated docs).
    """
    results: list[ExtractionResult] = []
    all_annotated: list = []
    for d in docs:
        result, annotated = run_extraction(
            text=d["text"],
            doc_name=d["name"],
            schema_name=schema_name,
            **kwargs,
        )
        results.append(result)
        if annotated:
            all_annotated.extend(annotated)
    return results, all_annotated


def format_extraction_index(results: list[ExtractionResult]) -> str:
    """Format extraction results as a plain-text index for RLM context."""
    lines = [
        "===== EXTRACTION INDEX =====",
        "Pre-extracted structured data with source document and character offsets.",
        "",
    ]

    for r in results:
        if r.error:
            lines.append(f"[Document: {r.doc_name}]  (extraction failed: {r.error})")
            lines.append("")
            continue
        if not r.extractions:
            lines.append(f"[Document: {r.doc_name}]  (no extractions found)")
            lines.append("")
            continue

        lines.append(f"[Document: {r.doc_name}]")
        for ext in r.extractions:
            attrs = ""
            if ext["attributes"]:
                attrs = f"  {ext['attributes']}"
            lines.append(
                f'  - {ext["extraction_class"]}: "{ext["extraction_text"]}" '
                f'(chars {ext["char_start"]}-{ext["char_end"]}){attrs}'
            )
        lines.append("")

    return "\n".join(lines)


def build_enriched_context(
    extraction_results: list[ExtractionResult],
    raw_context: str,
) -> str:
    """Combine extraction index with raw document context.

    Args:
        extraction_results: Results from run_batch_extraction.
        raw_context: Output from build_structured_context().
    """
    index = format_extraction_index(extraction_results)
    return index + "\n\n" + raw_context


def generate_visualization(
    annotated_docs: list,
    output_dir: str,
) -> str | None:
    """Generate HTML visualization from raw annotated documents.

    Returns path to HTML file, or None on failure.
    """
    if not annotated_docs:
        return None

    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        jsonl_name = "extraction_results.jsonl"
        lx.io.save_annotated_documents(annotated_docs, output_name=jsonl_name, output_dir=str(output_path))

        jsonl_path = str(output_path / jsonl_name)
        html_content = lx.visualize(jsonl_path)

        html_path = output_path / "extraction_viz.html"
        html_path.write_text(html_content, encoding="utf-8")
        return str(html_path)

    except Exception as e:
        logger.warning("Visualization generation failed: %s", e)
        return None
