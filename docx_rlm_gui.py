"""
RLM Document Chat - Desktop GUI Application

A chatbot-style interface for ingesting documents (.docx, .pdf, .txt)
and running RLM (Recursive Learning Model) queries against them.

Usage:
    uv run python docx_rlm_gui.py
"""

import io
import os
import sys


def _fix_windows_encoding():
    """Force UTF-8 on stdout/stderr to avoid charmap errors on Windows.

    Sets PYTHONIOENCODING so libraries like rich also pick up UTF-8,
    then rewraps stdout/stderr for the current process.
    """
    os.environ["PYTHONIOENCODING"] = "utf-8:replace"
    if sys.stdout and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True,
        )
    if sys.stderr and hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True,
        )


def main():
    _fix_windows_encoding()
    from gui.app import RLMChatApp
    app = RLMChatApp()
    app.mainloop()


if __name__ == "__main__":
    main()
