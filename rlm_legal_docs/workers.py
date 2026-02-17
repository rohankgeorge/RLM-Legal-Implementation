"""
Background thread workers for file ingestion and RLM queries.
Uses threading + queue + tkinter after() polling to keep the GUI responsive.
"""

import logging
import threading
import traceback
from pathlib import Path
from queue import Queue

from rlm_legal_docs.query import build_structured_context, run_query
from rlm_legal_docs.readers import extract_text

logger = logging.getLogger(__name__)


class IngestWorker:
    """Reads selected files in a background thread, builds structured context."""

    def __init__(
        self,
        files: list[Path],
        result_queue: Queue,
        extraction_config: dict | None = None,
    ):
        self.files = files
        self.result_queue = result_queue
        self.extraction_config = extraction_config
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            docs: list[dict[str, str]] = []
            errors: list[str] = []
            for fp in self.files:
                try:
                    text = extract_text(fp)
                    if text.strip():
                        docs.append({"name": fp.name, "text": text})
                    else:
                        errors.append(f"{fp.name}: no extractable text")
                except Exception as e:
                    errors.append(f"{fp.name}: {e}")

            if not docs:
                self.result_queue.put(
                    {
                        "type": "ingest_error",
                        "error": "No documents could be loaded.\n" + "\n".join(errors),
                    }
                )
                return

            raw_context = build_structured_context(docs)
            extraction_results = []
            viz_path = None

            if self.extraction_config and self.extraction_config.get("enabled"):
                extraction_results, viz_path = self._run_extraction(docs, errors)
                from rlm_legal_docs.extraction import build_enriched_context

                context = build_enriched_context(extraction_results, raw_context)
            else:
                context = raw_context

            self.result_queue.put(
                {
                    "type": "ingest_done",
                    "docs": docs,
                    "context": context,
                    "errors": errors,
                    "extraction_results": extraction_results,
                    "viz_path": viz_path,
                }
            )
        except Exception as e:
            self.result_queue.put(
                {
                    "type": "ingest_error",
                    "error": f"Ingestion failed: {e}\n{traceback.format_exc()}",
                }
            )

    def _run_extraction(
        self,
        docs: list[dict[str, str]],
        errors: list[str],
    ) -> tuple[list, str | None]:
        """Run LangExtract on ingested documents with caching."""
        from rlm_legal_docs.extraction import (
            generate_visualization,
            run_extraction,
        )
        from rlm_legal_docs.extraction_store import ExtractionStore

        cfg = self.extraction_config or {}
        schema = cfg.get("schema", "general")
        model_id = cfg.get("model_id", "gemini-2.5-flash")
        api_key = cfg.get("api_key")
        passes = cfg.get("passes", 2)

        store = ExtractionStore()
        extraction_results = []
        all_annotated = []

        for fp, doc_dict in zip(self.files, docs, strict=False):
            # Check cache first
            cached = store.get(str(fp), schema)
            if cached:
                extraction_results.append(cached)
                continue

            result, annotated = run_extraction(
                text=doc_dict["text"],
                doc_name=doc_dict["name"],
                schema_name=schema,
                model_id=model_id,
                api_key=api_key,
                extraction_passes=passes,
            )
            extraction_results.append(result)
            if annotated:
                all_annotated.extend(annotated)

            if result.error:
                errors.append(f"{doc_dict['name']}: extraction warning - {result.error}")
            else:
                store.put(str(fp), schema, result)

        # Generate visualization
        viz_path = None
        if all_annotated:
            viz_path = generate_visualization(
                all_annotated, str(Path(store._dir) / "viz")
            )

        return extraction_results, viz_path


class QueryWorker:
    """Runs an RLM query in a background thread."""

    def __init__(
        self,
        rlm,
        context: str,
        query: str,
        result_queue: Queue,
        logger=None,
        extraction_results: list | None = None,
    ):
        self.rlm = rlm
        self.context = context
        self.query = query
        self.result_queue = result_queue
        self.logger = logger
        self.extraction_results = extraction_results or []
        self._thread: threading.Thread | None = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        # Record iteration count before query so we can extract the right range
        start_iter = self.logger.iteration_count if self.logger else 0
        try:
            response = run_query(self.rlm, self.context, self.query)
            end_iter = self.logger.iteration_count if self.logger else 0

            # Citation enrichment (best-effort, never blocks response)
            enriched = None
            if self.extraction_results:
                try:
                    from rlm_legal_docs.citations import CitationEnricher

                    enricher = CitationEnricher(self.extraction_results)
                    enriched = enricher.enrich(response)
                except Exception:
                    logger.debug("Citation enrichment failed", exc_info=True)

            result = {
                "type": "query_done",
                "query": self.query,
                "response": response,
                "enriched": enriched,
            }
            if self.logger:
                result["log_file"] = self.logger.log_file_path
                result["log_start_iter"] = start_iter
                result["log_end_iter"] = end_iter
            self.result_queue.put(result)
        except Exception as e:
            self.result_queue.put(
                {
                    "type": "query_error",
                    "query": self.query,
                    "error": f"Query failed: {e}\n{traceback.format_exc()}",
                }
            )
