"""
DOCX Folder Ingestion + RLM Query Script

Ingests all .docx files from a specified folder, extracts and structures
their text content, then runs RLM (Recursive Learning Model) queries
against the combined corpus.

Usage:
    uv run python docx_rlm_query.py --folder ./my_docs --query "Summarize the key findings"
    uv run python docx_rlm_query.py --folder ./my_docs --queries queries.txt
    uv run python docx_rlm_query.py --folder ./my_docs --interactive

Requirements:
    uv add python-docx
"""

import argparse
import os
import sys
from pathlib import Path

from docx import Document
from rlm import RLM
from rlm.logger import RLMLogger

# ---------------------------------------------------------------------------
# DOCX ingestion
# ---------------------------------------------------------------------------


def extract_text_from_docx(filepath: Path) -> str:
    """Extract all paragraph text from a single .docx file."""
    doc = Document(str(filepath))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def ingest_folder(folder: Path) -> list[dict[str, str]]:
    """Walk *folder* and return a list of {name, text} dicts for every .docx."""
    docs: list[dict[str, str]] = []
    docx_files = sorted(folder.glob("*.docx"))

    if not docx_files:
        print(f"No .docx files found in {folder}")
        sys.exit(1)

    for fp in docx_files:
        print(f"  Reading: {fp.name}")
        text = extract_text_from_docx(fp)
        if text:
            docs.append({"name": fp.name, "text": text})
        else:
            print(f"  Warning: {fp.name} contained no extractable text, skipping.")

    return docs


def build_structured_context(docs: list[dict[str, str]]) -> str:
    """Concatenate extracted documents into a structured plaintext context."""
    sections: list[str] = []
    for i, doc in enumerate(docs, 1):
        sections.append(f"===== DOCUMENT {i}: {doc['name']} =====\n\n{doc['text']}")
    header = (
        f"The following context contains {len(docs)} document(s) "
        "extracted from DOCX files.\n"
        "Each document is delimited by ===== DOCUMENT N: <filename> =====.\n"
    )
    return header + "\n\n" + "\n\n".join(sections)


# ---------------------------------------------------------------------------
# RLM session
# ---------------------------------------------------------------------------


def create_rlm(args: argparse.Namespace) -> RLM:
    """Build an RLM instance from CLI arguments."""
    backend_kwargs: dict = {"model_name": args.model}

    # Resolve API key: explicit flag > env var
    api_key = args.api_key or os.getenv(f"{args.backend.upper()}_API_KEY")
    if not api_key:
        # Try common fallback env var names
        fallbacks = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
        }
        env_name = fallbacks.get(args.backend, f"{args.backend.upper()}_API_KEY")
        api_key = os.getenv(env_name)

    if not api_key:
        print(f"Error: No API key found. Set {args.backend.upper()}_API_KEY or pass --api-key.")
        sys.exit(1)

    backend_kwargs["api_key"] = api_key

    logger = RLMLogger(log_dir=args.log_dir) if args.log_dir else None

    # Build system prompt with extraction context if enabled
    custom_prompt = None
    if args.extract:
        from rlm_legal_docs.prompts import build_system_prompt

        custom_prompt = build_system_prompt(extraction_enabled=True)

    return RLM(
        backend=args.backend,
        backend_kwargs=backend_kwargs,
        environment="local",
        max_depth=args.max_depth,
        max_iterations=args.max_iterations,
        custom_system_prompt=custom_prompt,
        logger=logger,
        verbose=args.verbose,
        persistent=True,
    )


def run_query(rlm: RLM, context: str, query: str) -> str:
    """Run a single RLM query against the document context."""
    result = rlm.completion(prompt=context, root_prompt=query)
    return result.response


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Ingest DOCX files and run RLM queries against them.",
    )

    # --- document source ---
    p.add_argument(
        "--folder",
        type=Path,
        required=True,
        help="Path to folder containing .docx files.",
    )

    # --- query source (mutually exclusive) ---
    qgroup = p.add_mutually_exclusive_group(required=True)
    qgroup.add_argument(
        "--query",
        "-q",
        type=str,
        help="Single query string to run.",
    )
    qgroup.add_argument(
        "--queries",
        type=Path,
        help="Path to a text file with one query per line.",
    )
    qgroup.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Enter an interactive query loop.",
    )

    # --- RLM / LLM config ---
    p.add_argument("--backend", default="openai", help="LLM backend (default: openai).")
    p.add_argument("--model", default="gpt-4o", help="Model name (default: gpt-4o).")
    p.add_argument("--api-key", default=None, help="API key (or set via env var).")
    p.add_argument("--max-depth", type=int, default=1, help="RLM max recursion depth.")
    p.add_argument("--max-iterations", type=int, default=30, help="RLM max iterations.")
    p.add_argument("--log-dir", type=str, default=None, help="Directory for RLM logs.")
    p.add_argument("--verbose", "-v", action="store_true", help="Print RLM progress.")

    # --- Extraction ---
    p.add_argument(
        "--extract",
        action="store_true",
        default=False,
        help="Enable LangExtract preprocessing.",
    )
    p.add_argument("--no-extract", dest="extract", action="store_false")
    p.add_argument(
        "--extract-model",
        default="gemini-2.5-flash",
        help="LangExtract model (default: gemini-2.5-flash).",
    )
    p.add_argument(
        "--extract-schema",
        default="general",
        choices=["general", "contract"],
        help="Extraction schema (default: general).",
    )
    p.add_argument(
        "--extract-api-key",
        default=None,
        help="LangExtract API key (or set LANGEXTRACT_API_KEY env var).",
    )
    p.add_argument(
        "--extract-passes",
        type=int,
        default=2,
        help="Number of extraction passes (default: 2).",
    )

    return p.parse_args()


def main() -> None:
    args = parse_args()

    # --- 1. Ingest documents ---
    folder = args.folder.resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory.")
        sys.exit(1)

    print(f"\n[1/3] Ingesting DOCX files from: {folder}\n")
    docs = ingest_folder(folder)
    context = build_structured_context(docs)
    print(f"\n  Loaded {len(docs)} document(s)  ({len(context):,} chars total)\n")

    # --- 1.5 Run extraction if enabled ---
    if args.extract:
        from rlm_legal_docs.extraction import build_enriched_context, run_batch_extraction

        print("[1.5/3] Running LangExtract extraction...\n")
        api_key = args.extract_api_key or os.getenv("LANGEXTRACT_API_KEY")
        results, _annotated = run_batch_extraction(
            docs,
            schema_name=args.extract_schema,
            model_id=args.extract_model,
            api_key=api_key,
            extraction_passes=args.extract_passes,
        )
        context = build_enriched_context(results, context)

        total = sum(len(r.extractions) for r in results if not r.error)
        errors = sum(1 for r in results if r.error)
        print(f"  Extracted {total} entities from {len(results)} doc(s)")
        if errors:
            print(f"  ({errors} document(s) had extraction errors)")
        print()

    # --- 2. Create RLM instance ---
    print("[2/3] Initialising RLM...\n")
    rlm = create_rlm(args)

    # --- 3. Run queries ---
    print("[3/3] Running queries...\n")
    try:
        if args.query:
            # Single query mode
            print(f"  Q: {args.query}\n")
            answer = run_query(rlm, context, args.query)
            print(f"  A: {answer}\n")

        elif args.queries:
            # Batch mode – one query per line
            lines = [
                line.strip()
                for line in args.queries.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            ]
            for idx, query in enumerate(lines, 1):
                print(f"  [{idx}/{len(lines)}] Q: {query}\n")
                answer = run_query(rlm, context, query)
                print(f"  A: {answer}\n")
                print("-" * 60)

        elif args.interactive:
            # Interactive REPL
            print("  Entering interactive mode. Type 'exit' or 'quit' to stop.\n")
            while True:
                try:
                    query = input("  Q: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if query.lower() in ("exit", "quit", ""):
                    break
                answer = run_query(rlm, context, query)
                print(f"\n  A: {answer}\n")

    finally:
        rlm.close()

    print("Done.")


if __name__ == "__main__":
    main()
