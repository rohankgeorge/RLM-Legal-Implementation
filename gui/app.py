"""
Main application window for RLM Document Chat.
Wires together the file selector, config sidebar, and chat frame.
"""

import os
import tempfile
from queue import Queue

import customtkinter as ctk

from gui.chat_frame import ChatFrame
from gui.config_frame import ConfigFrame
from gui.constants import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_LARGE,
    FONT_SIZE_SMALL,
    POLL_INTERVAL_MS,
    SIDEBAR_WIDTH,
)
from gui.file_frame import FileFrame
from gui.workers import IngestWorker, QueryWorker

from rlm import RLM
from rlm.logger import RLMLogger
from rlm.utils.prompts import RLM_SYSTEM_PROMPT


class RLMChatApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("RLM Document Chat")
        self.geometry("1200x800")
        self.minsize(900, 600)

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Configure window colors
        self.configure(fg_color=COLORS["bg_dark"])

        # State
        self._rlm: RLM | None = None
        self._logger: RLMLogger | None = None
        self._log_dir: str = tempfile.mkdtemp(prefix="rlm_gui_logs_")
        self._context: str = ""
        self._result_queue: Queue = Queue()
        self._query_active = False

        # Build UI
        self._build_ui()

        # Start polling
        self.after(POLL_INTERVAL_MS, self._poll_results)

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        # --- Title bar ---
        title_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], height=45)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        ctk.CTkLabel(
            title_frame,
            text="  RLM Document Chat",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(side="left", padx=10, pady=8)

        # --- Main content area ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        # --- Sidebar (left) ---
        sidebar = ctk.CTkFrame(content_frame, fg_color=COLORS["bg_dark"],
                                width=SIDEBAR_WIDTH, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # File selection (top of sidebar)
        self.file_frame = FileFrame(sidebar)
        self.file_frame.pack(fill="x")

        # Config (bottom of sidebar, scrollable)
        self.config_frame = ConfigFrame(
            sidebar,
            on_start_session=self._on_start_session,
            on_reset_session=self._on_reset_session,
        )
        self.config_frame.pack(fill="both", expand=True)

        # --- Sidebar separator ---
        sep = ctk.CTkFrame(content_frame, fg_color=COLORS["border"], width=1)
        sep.pack(side="left", fill="y")

        # --- Chat area (right) ---
        self.chat_frame = ChatFrame(content_frame, on_send=self._on_send_query)
        self.chat_frame.pack(side="left", fill="both", expand=True)

        # --- Status bar ---
        self.status_bar = ctk.CTkLabel(
            self,
            text="  Status: Ready",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["muted"],
            fg_color=COLORS["bg_medium"],
            anchor="w",
            height=28,
        )
        self.status_bar.pack(fill="x", side="bottom")

    def _update_status(self, text: str):
        self.status_bar.configure(text=f"  {text}")

    def _on_start_session(self):
        """Handle Start Session button click."""
        # Get checked files
        files = self.file_frame.get_checked_files()
        if not files:
            self.chat_frame.add_error_message("No files selected. Please select documents first.")
            return

        # Get config
        config = self.config_frame.get_config()
        if not config["api_key"]:
            self.chat_frame.add_error_message(
                f"No API key provided for {config['backend']}. "
                f"Enter it in the sidebar or set {config['backend'].upper()}_API_KEY environment variable."
            )
            return

        # Disable UI during ingestion
        self.config_frame.set_status("Ingesting files...")
        self._update_status("Status: Ingesting documents...")
        self.config_frame.start_btn.configure(state="disabled")
        self.file_frame.set_enabled(False)

        # Start ingestion worker
        worker = IngestWorker(files, self._result_queue)
        worker.start()

    def _create_rlm(self, config: dict) -> RLM:
        """Create an RLM instance from the GUI config."""
        backend_kwargs = {
            "model_name": config["model"],
            "api_key": config["api_key"],
        }

        # Custom instructions
        custom_prompt = None
        if config.get("custom_instructions"):
            custom_prompt = config["custom_instructions"] + "\n\n" + RLM_SYSTEM_PROMPT

        # Sub-query model
        other_backends = None
        other_backend_kwargs = None
        if "sub_query" in config:
            sub = config["sub_query"]
            other_backends = [sub["backend"]]
            other_backend_kwargs = [{
                "model_name": sub["model"],
                "api_key": sub["api_key"],
            }]

        # Create logger for execution tracing
        self._logger = RLMLogger(log_dir=self._log_dir)

        return RLM(
            backend=config["backend"],
            backend_kwargs=backend_kwargs,
            environment="local",
            max_depth=config["max_depth"],
            max_iterations=config["max_iterations"],
            custom_system_prompt=custom_prompt,
            other_backends=other_backends,
            other_backend_kwargs=other_backend_kwargs,
            logger=self._logger,
            verbose=False,  # Rich console can't handle Unicode on Windows charmap
            persistent=True,
        )

    def _on_reset_session(self):
        """Handle Reset Session button click."""
        if self._rlm is not None:
            try:
                self._rlm.close()
            except Exception:
                pass
            self._rlm = None
        self._logger = None
        self._context = ""
        self._query_active = False

        # Reset UI
        self.config_frame.set_session_active(False)
        self.config_frame.set_status("No session")
        self.file_frame.set_enabled(True)
        self.chat_frame.set_input_enabled(False)
        self.chat_frame.clear_chat()
        self._update_status("Status: Ready")

    def _on_send_query(self, query: str):
        """Handle sending a query from the chat input."""
        if self._rlm is None or not self._context:
            self.chat_frame.add_error_message("No active session. Click 'Start Session' first.")
            return
        if self._query_active:
            return

        self._query_active = True
        self.chat_frame.show_thinking()
        self.chat_frame.set_input_enabled(False)
        self._update_status("Status: Processing query...")

        worker = QueryWorker(self._rlm, self._context, query, self._result_queue,
                             logger=self._logger)
        worker.start()

    def _poll_results(self):
        """Poll the result queue for worker completions."""
        while not self._result_queue.empty():
            result = self._result_queue.get_nowait()
            msg_type = result.get("type")

            if msg_type == "ingest_done":
                self._handle_ingest_done(result)
            elif msg_type == "ingest_error":
                self._handle_ingest_error(result)
            elif msg_type == "query_done":
                self._handle_query_done(result)
            elif msg_type == "query_error":
                self._handle_query_error(result)

        self.after(POLL_INTERVAL_MS, self._poll_results)

    def _handle_ingest_done(self, result: dict):
        docs = result["docs"]
        context = result["context"]
        errors = result.get("errors", [])

        self._context = context

        # Create RLM instance
        config = self.config_frame.get_config()
        try:
            self._rlm = self._create_rlm(config)
        except Exception as e:
            self.chat_frame.add_error_message(f"Failed to create RLM instance: {e}")
            self.config_frame.start_btn.configure(state="normal")
            self.file_frame.set_enabled(True)
            return

        # Update UI
        doc_count = len(docs)
        char_count = len(context)
        status_text = f"{doc_count} doc(s), {char_count:,} chars"
        self.config_frame.set_session_active(True)
        self.config_frame.set_status(status_text)
        self.chat_frame.set_input_enabled(True)
        self._update_status(
            f"Status: Session active | {config['backend']}/{config['model']} | {status_text}"
        )

        # Show success in chat
        msg = f"Session started! Loaded {doc_count} document(s) ({char_count:,} characters)."
        if errors:
            msg += "\n\nWarnings:\n" + "\n".join(f"  - {e}" for e in errors)
        msg += "\n\nYou can now ask questions about your documents."
        self.chat_frame.add_rlm_message(msg)

    def _handle_ingest_error(self, result: dict):
        self.chat_frame.add_error_message(result["error"])
        self.config_frame.start_btn.configure(state="normal")
        self.config_frame.set_status("Ingestion failed")
        self.file_frame.set_enabled(True)
        self._update_status("Status: Ready")

    def _handle_query_done(self, result: dict):
        self.chat_frame.add_rlm_message(
            result["response"],
            log_file=result.get("log_file"),
            log_start_iter=result.get("log_start_iter", 0),
            log_end_iter=result.get("log_end_iter"),
        )
        self._query_active = False
        self.chat_frame.set_input_enabled(True)
        config = self.config_frame.get_config()
        self._update_status(
            f"Status: Session active | {config['backend']}/{config['model']}"
        )

    def _handle_query_error(self, result: dict):
        self.chat_frame.add_error_message(result["error"])
        self._query_active = False
        self.chat_frame.set_input_enabled(True)
        self._update_status("Status: Query failed - ready for next question")

    def _on_close(self):
        """Clean up on window close."""
        if self._rlm is not None:
            try:
                self._rlm.close()
            except Exception:
                pass
        self.destroy()
