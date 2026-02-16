"""
File/folder selection frame with checkable file list.
"""

from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from rlm_legal_docs.constants import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SMALL,
    SUPPORTED_EXTENSIONS,
)


class FileFrame(ctk.CTkFrame):
    """Sidebar panel for selecting and listing files."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_dark"], **kwargs)

        self._file_checks: dict[str, ctk.BooleanVar] = {}  # filepath -> BooleanVar
        self._file_paths: list[Path] = []

        # --- Header ---
        header = ctk.CTkLabel(
            self,
            text="Loaded Documents",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        )
        header.pack(fill="x", padx=10, pady=(10, 5))

        # --- Button row ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.folder_btn = ctk.CTkButton(
            btn_frame,
            text="Select Folder",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["border"],
            text_color=COLORS["white"],
            width=130,
            height=28,
            command=self._on_select_folder,
        )
        self.folder_btn.pack(side="left", padx=(0, 5))

        self.files_btn = ctk.CTkButton(
            btn_frame,
            text="Select Files",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["border"],
            text_color=COLORS["white"],
            width=130,
            height=28,
            command=self._on_select_files,
        )
        self.files_btn.pack(side="left")

        # --- Path label ---
        self.path_label = ctk.CTkLabel(
            self,
            text="No files selected",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=280,
        )
        self.path_label.pack(fill="x", padx=10, pady=(0, 5))

        # --- Scrollable file checklist ---
        self.file_list_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_medium"],
            height=200,
        )
        self.file_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_select_folder(self):
        folder = filedialog.askdirectory(title="Select Document Folder")
        if not folder:
            return
        folder_path = Path(folder)
        files = sorted(
            f
            for f in folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        if files:
            self.path_label.configure(text=str(folder_path))
            self._set_files(files)
        else:
            self.path_label.configure(text="No supported files found in folder")

    def _on_select_files(self):
        filetypes = [
            ("Supported Files", "*.docx *.pdf *.txt"),
            ("Word Documents", "*.docx"),
            ("PDF Files", "*.pdf"),
            ("Text Files", "*.txt"),
        ]
        selected = filedialog.askopenfilenames(
            title="Select Document Files",
            filetypes=filetypes,
        )
        if not selected:
            return
        files = [Path(f) for f in selected]
        # Merge with existing files (avoid duplicates)
        existing = {str(p) for p in self._file_paths}
        for f in files:
            if str(f) not in existing:
                self._file_paths.append(f)
        self.path_label.configure(text=f"{len(self._file_paths)} file(s) selected")
        self._rebuild_checklist()

    def _set_files(self, files: list[Path]):
        """Replace the file list with a new set of files."""
        self._file_paths = list(files)
        self._rebuild_checklist()

    def _rebuild_checklist(self):
        """Rebuild the checkbox list from self._file_paths."""
        # Clear existing widgets
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        self._file_checks.clear()

        for fp in self._file_paths:
            var = ctk.BooleanVar(value=True)
            self._file_checks[str(fp)] = var

            cb = ctk.CTkCheckBox(
                self.file_list_frame,
                text=f" {fp.name}",
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                hover_color=COLORS["accent"],
                variable=var,
            )
            cb.pack(fill="x", padx=5, pady=2, anchor="w")

    def get_checked_files(self) -> list[Path]:
        """Return list of file paths that are currently checked."""
        return [Path(fp_str) for fp_str, var in self._file_checks.items() if var.get()]

    def get_file_count(self) -> int:
        """Return the number of checked files."""
        return sum(1 for var in self._file_checks.values() if var.get())

    def set_enabled(self, enabled: bool):
        """Enable or disable file selection buttons."""
        state = "normal" if enabled else "disabled"
        self.folder_btn.configure(state=state)
        self.files_btn.configure(state=state)
