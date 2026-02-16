"""Lightweight file-based cache for extraction results.

Stores extraction results as JSON files so documents do not need
to be re-extracted on every session.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict
from pathlib import Path

from rlm_legal_docs.extraction import ExtractionResult

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = "~/.rlm_extractions"


class ExtractionStore:
    """Simple JSON file cache for ExtractionResult objects.

    Cache key is derived from file path, modification time, and schema name.
    When a file changes on disk, the mtime changes and the old cache entry
    is automatically bypassed (a new key is computed).
    """

    def __init__(self, cache_dir: str = DEFAULT_CACHE_DIR):
        self._dir = Path(cache_dir).expanduser()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key(self, file_path: str, schema_name: str) -> str:
        """Compute cache key from file path, mtime, and schema."""
        p = Path(file_path)
        mtime = str(p.stat().st_mtime) if p.exists() else "0"
        raw = f"{file_path}|{mtime}|{schema_name}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, file_path: str, schema_name: str) -> ExtractionResult | None:
        """Retrieve cached extraction result, or None on cache miss."""
        try:
            cache_file = self._dir / f"{self._key(file_path, schema_name)}.json"
            if not cache_file.exists():
                return None
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return ExtractionResult(**data)
        except Exception:
            logger.debug("Cache read failed for %s", file_path)
            return None

    def put(self, file_path: str, schema_name: str, result: ExtractionResult) -> None:
        """Write extraction result to cache."""
        try:
            cache_file = self._dir / f"{self._key(file_path, schema_name)}.json"
            cache_file.write_text(json.dumps(asdict(result)), encoding="utf-8")
        except Exception:
            logger.debug("Cache write failed for %s", file_path)

    def clear(self) -> None:
        """Remove all cached extraction results."""
        for f in self._dir.glob("*.json"):
            f.unlink(missing_ok=True)
