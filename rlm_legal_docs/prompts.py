"""System prompt components for extraction-aware RLM sessions.

Provides the enriched system prompt that instructs the RLM about
the extraction index format, citation requirements, and available
tools for on-demand extraction.
"""

from __future__ import annotations

EXTRACTION_CONTEXT_PROMPT = """\
CONTEXT STRUCTURE
=================
The context variable contains two sections:

1. EXTRACTION INDEX: Pre-extracted structured data from the document corpus.
   Each entry includes the document name, extraction class, extracted text,
   and character offsets (char_start-char_end) in the source document.
   Use this section to plan your analysis and locate specific facts quickly.

2. RAW DOCUMENTS: Full text of each document, delimited by
   ===== DOCUMENT N: <filename> =====
   Use this section when you need to read surrounding context, verify
   extractions, or find information not covered by the extraction index.

CITATION REQUIREMENTS
=====================
When making factual claims, include inline citations using this format:
  [Source: document_name, chars start-end]

For claims derived from the extraction index, use the character offsets
provided. For claims found by reading the raw text, determine the
approximate character offset.

For analytical or inferential statements (comparisons, risk assessments,
recommendations), prefix with [Analysis] to distinguish from grounded facts.

AVAILABLE TOOLS
===============
The `langextract` library is available in this REPL (import langextract as lx).
If the user's query requires extraction of entity types not present in the
extraction index, you can run on-demand extraction:

  import langextract as lx
  results = lx.extract(
      text_or_documents=text_to_extract_from,
      prompt_description="Extract all [entity type] from this text",
      examples=[],
      model_id="gemini-2.5-flash",
  )
  for doc in results:
      for ext in doc.extractions:
          print(f"{ext.extraction_class}: {ext.extraction_text} "
                f"(chars {ext.char_interval[0]}-{ext.char_interval[1]})")

IMPORTANT: LangExtract output can be verbose. Always summarize results
before printing. Do not print raw annotated document objects directly.
"""


def build_system_prompt(
    extraction_enabled: bool,
    custom_instructions: str | None = None,
    base_prompt: str = "",
) -> str:
    """Compose the full system prompt for the RLM.

    Ordering: extraction instructions -> custom user instructions -> base RLM prompt.

    Args:
        extraction_enabled: Whether extraction was run during ingestion.
        custom_instructions: User-provided custom instructions from the GUI.
        base_prompt: The default RLM system prompt (RLM_SYSTEM_PROMPT).
    """
    parts: list[str] = []
    if extraction_enabled:
        parts.append(EXTRACTION_CONTEXT_PROMPT)
    if custom_instructions:
        parts.append(custom_instructions)
    if base_prompt:
        parts.append(base_prompt)
    return "\n\n".join(parts) if parts else base_prompt
