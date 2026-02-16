"""
Log Viewer window for viewing RLM execution traces.
Parses .jsonl log files and displays metadata + per-iteration details.
"""

import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import customtkinter as ctk

from gui.constants import COLORS, FONT_FAMILY, FONT_SIZE, FONT_SIZE_SMALL, FONT_SIZE_LARGE


def parse_log_file(log_path: str, start_iter: int = 0, end_iter: int | None = None) -> list[dict]:
    """Read a .jsonl log file and return entries in the given iteration range."""
    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("type") == "metadata":
                entries.append(entry)
            elif entry.get("type") == "iteration":
                iter_num = entry.get("iteration", 0)
                if iter_num > start_iter and (end_iter is None or iter_num <= end_iter):
                    entries.append(entry)
    return entries


def format_log_as_text(entries: list[dict]) -> str:
    """Format parsed log entries as readable plain text."""
    lines = []
    for entry in entries:
        if entry.get("type") == "metadata":
            lines.append("=" * 60)
            lines.append("RLM EXECUTION LOG - METADATA")
            lines.append("=" * 60)
            for key in ("backend", "model", "environment", "max_depth", "max_iterations"):
                if key in entry:
                    lines.append(f"  {key}: {entry[key]}")
            lines.append("")
        elif entry.get("type") == "iteration":
            iter_num = entry.get("iteration", "?")
            time_s = entry.get("iteration_time", 0)
            lines.append("-" * 60)
            lines.append(f"ITERATION {iter_num}  ({time_s:.2f}s)")
            lines.append("-" * 60)

            # Model response
            response = entry.get("model_response", "")
            if response:
                lines.append("\n[Model Response]")
                lines.append(response[:2000])
                if len(response) > 2000:
                    lines.append(f"... ({len(response)} chars total)")

            # Code blocks
            code_blocks = entry.get("code_blocks", [])
            for i, cb in enumerate(code_blocks, 1):
                lines.append(f"\n[Code Block {i}]")
                lines.append(cb.get("code", ""))
                stdout = cb.get("result", {}).get("stdout", "")
                stderr = cb.get("result", {}).get("stderr", "")
                if stdout:
                    lines.append(f"  stdout: {stdout[:500]}")
                if stderr:
                    lines.append(f"  stderr: {stderr[:500]}")

            # Sub-calls
            sub_calls = entry.get("sub_llm_calls", [])
            for i, sc in enumerate(sub_calls, 1):
                lines.append(f"\n[Sub-Call {i}] model={sc.get('model', '?')}  ({sc.get('time', 0):.2f}s)")
                prompt = sc.get("prompt", "")
                if prompt:
                    lines.append(f"  Prompt: {prompt[:300]}...")
                resp = sc.get("response", "")
                if resp:
                    lines.append(f"  Response: {resp[:300]}...")

            # Final answer
            final = entry.get("final_answer")
            if final:
                lines.append(f"\n[Final Answer Found]")
                lines.append(final[:1000])

            lines.append("")
    return "\n".join(lines)


class CollapsibleSection(ctk.CTkFrame):
    """A collapsible section with a toggle header."""

    def __init__(self, master, title: str, content_text: str, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_medium"], corner_radius=6, **kwargs)

        self._expanded = False
        self._content_text = content_text

        # Header button
        self._header = ctk.CTkButton(
            self,
            text=f"+ {title}",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            fg_color="transparent",
            hover_color=COLORS["bg_light"],
            text_color=COLORS["text"],
            anchor="w",
            command=self._toggle,
        )
        self._header.pack(fill="x", padx=4, pady=2)

        # Content textbox (initially hidden)
        self._content = ctk.CTkTextbox(
            self,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_dark"],
            text_color=COLORS["white"],
            wrap="word",
            height=150,
            border_width=1,
            border_color=COLORS["border"],
        )
        self._content.insert("1.0", content_text)
        self._content.configure(state="disabled")

    def _toggle(self):
        self._expanded = not self._expanded
        title = self._header.cget("text")
        if self._expanded:
            self._header.configure(text=title.replace("+ ", "- ", 1))
            self._content.pack(fill="x", padx=8, pady=(0, 6))
        else:
            self._header.configure(text=title.replace("- ", "+ ", 1))
            self._content.pack_forget()


class LogViewerWindow(ctk.CTkToplevel):
    """Window that displays parsed RLM execution log."""

    def __init__(self, master, log_path: str, start_iter: int = 0, end_iter: int | None = None):
        super().__init__(master)

        self.title("RLM Execution Log")
        self.geometry("800x700")
        self.minsize(600, 400)
        self.configure(fg_color=COLORS["bg_dark"])

        self._log_path = log_path
        self._entries = parse_log_file(log_path, start_iter, end_iter)

        self._build_ui()

    def _build_ui(self):
        # --- Top toolbar ---
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], height=40)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        ctk.CTkLabel(
            toolbar,
            text="  Execution Log",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(side="left", padx=6, pady=6)

        ctk.CTkButton(
            toolbar,
            text="Save Log",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            width=80,
            command=self._save_log,
        ).pack(side="right", padx=4, pady=6)

        ctk.CTkButton(
            toolbar,
            text="Copy All",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["border"],
            text_color=COLORS["text"],
            width=80,
            command=self._copy_all,
        ).pack(side="right", padx=4, pady=6)

        # --- Scrollable content ---
        self._scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"])
        self._scroll.pack(fill="both", expand=True, padx=6, pady=6)

        self._populate()

    def _populate(self):
        """Build collapsible sections from parsed entries."""
        if not self._entries:
            ctk.CTkLabel(
                self._scroll,
                text="No log entries found for this query.",
                font=(FONT_FAMILY, FONT_SIZE),
                text_color=COLORS["muted"],
            ).pack(padx=20, pady=20)
            return

        for entry in self._entries:
            if entry.get("type") == "metadata":
                self._add_metadata_section(entry)
            elif entry.get("type") == "iteration":
                self._add_iteration_section(entry)

    def _add_metadata_section(self, entry: dict):
        """Add a metadata summary section."""
        info_parts = []
        for key in ("backend", "model", "environment", "max_depth", "max_iterations"):
            if key in entry:
                info_parts.append(f"{key}: {entry[key]}")
        text = "\n".join(info_parts) if info_parts else "(no metadata)"

        section = CollapsibleSection(self._scroll, title="Metadata / Config", content_text=text)
        section.pack(fill="x", padx=4, pady=3)
        # Auto-expand metadata
        section._toggle()

    def _add_iteration_section(self, entry: dict):
        """Add an iteration section with sub-sections."""
        iter_num = entry.get("iteration", "?")
        time_s = entry.get("iteration_time", 0)
        has_final = bool(entry.get("final_answer"))
        suffix = "  [FINAL ANSWER]" if has_final else ""
        title = f"Iteration {iter_num}  ({time_s:.2f}s){suffix}"

        # Build combined content for iteration
        parts = []

        # Model response
        response = entry.get("model_response", "")
        if response:
            parts.append("[Model Response]")
            parts.append(response)
            parts.append("")

        # Code blocks
        code_blocks = entry.get("code_blocks", [])
        for i, cb in enumerate(code_blocks, 1):
            parts.append(f"[Code Block {i}]")
            parts.append(cb.get("code", ""))
            result = cb.get("result", {})
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")
            if stdout:
                parts.append(f"--- stdout ---\n{stdout}")
            if stderr:
                parts.append(f"--- stderr ---\n{stderr}")
            parts.append("")

        # Sub-LLM calls
        sub_calls = entry.get("sub_llm_calls", [])
        for i, sc in enumerate(sub_calls, 1):
            model = sc.get("model", "?")
            sc_time = sc.get("time", 0)
            parts.append(f"[Sub-Call {i}] model={model}  ({sc_time:.2f}s)")
            prompt = sc.get("prompt", "")
            if prompt:
                parts.append(f"Prompt:\n{prompt}")
            resp = sc.get("response", "")
            if resp:
                parts.append(f"Response:\n{resp}")
            parts.append("")

        # Final answer
        final = entry.get("final_answer")
        if final:
            parts.append("[Final Answer]")
            parts.append(final)

        content = "\n".join(parts) if parts else "(empty iteration)"

        section = CollapsibleSection(self._scroll, title=title, content_text=content)
        section.pack(fill="x", padx=4, pady=3)

    def _save_log(self):
        """Save the .jsonl file to a user-chosen location."""
        dest = filedialog.asksaveasfilename(
            parent=self,
            title="Save Execution Log",
            defaultextension=".jsonl",
            filetypes=[("JSON Lines", "*.jsonl"), ("All Files", "*.*")],
            initialfile=Path(self._log_path).name,
        )
        if not dest:
            return
        import shutil
        shutil.copy2(self._log_path, dest)

    def _copy_all(self):
        """Copy formatted text summary to clipboard."""
        text = format_log_as_text(self._entries)
        self.clipboard_clear()
        self.clipboard_append(text)
