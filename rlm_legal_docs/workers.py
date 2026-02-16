"""
Background thread workers for file ingestion and RLM queries.
Uses threading + queue + tkinter after() polling to keep the GUI responsive.
"""

import threading
import traceback
from pathlib import Path
from queue import Queue

from docx import Document
from docx_rlm_query import build_structured_context, run_query
from PyPDF2 import PdfReader


def extract_text_from_docx(filepath: Path) -> str:
    """Extract all paragraph text from a single .docx file."""
    doc = Document(str(filepath))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_pdf(filepath: Path) -> str:
    """Extract text from all pages of a PDF file."""
    reader = PdfReader(str(filepath))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_txt(filepath: Path) -> str:
    """Read plain text file."""
    return filepath.read_text(encoding="utf-8")


def extract_text(filepath: Path) -> str:
    """Dispatch to the correct extraction function based on file extension."""
    ext = filepath.suffix.lower()
    if ext == ".docx":
        return extract_text_from_docx(filepath)
    elif ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext == ".txt":
        return extract_text_from_txt(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


class IngestWorker:
    """Reads selected files in a background thread, builds structured context."""

    def __init__(self, files: list[Path], result_queue: Queue):
        self.files = files
        self.result_queue = result_queue
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

            context = build_structured_context(docs)
            self.result_queue.put(
                {
                    "type": "ingest_done",
                    "docs": docs,
                    "context": context,
                    "errors": errors,
                }
            )
        except Exception as e:
            self.result_queue.put(
                {
                    "type": "ingest_error",
                    "error": f"Ingestion failed: {e}\n{traceback.format_exc()}",
                }
            )


class QueryWorker:
    """Runs an RLM query in a background thread."""

    def __init__(self, rlm, context: str, query: str, result_queue: Queue, logger=None):
        self.rlm = rlm
        self.context = context
        self.query = query
        self.result_queue = result_queue
        self.logger = logger
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
            result = {
                "type": "query_done",
                "query": self.query,
                "response": response,
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
