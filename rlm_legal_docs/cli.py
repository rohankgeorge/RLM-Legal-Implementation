"""CLI entry points for RLM Legal Document Tools."""

import io
import os
import sys


def _fix_windows_encoding():
    """Force UTF-8 on stdout/stderr to avoid charmap errors on Windows."""
    os.environ["PYTHONIOENCODING"] = "utf-8:replace"
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )


def run_gui():
    """Entry point for GUI application."""
    _fix_windows_encoding()
    from rlm_legal_docs.app import RLMChatApp

    app = RLMChatApp()
    app.mainloop()


def run_query():
    """Entry point for CLI query tool."""
    _fix_windows_encoding()
    from rlm_legal_docs.query import main

    main()
