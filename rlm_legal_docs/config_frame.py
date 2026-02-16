"""
RLM configuration sidebar frame.
Includes primary model, sub-query model, custom instructions, and session controls.
"""

import json
import os
from pathlib import Path

import customtkinter as ctk

from rlm_legal_docs.constants import (
    BACKENDS,
    COLORS,
    CONFIG_FILE,
    DEFAULT_MODEL,
    DEFAULT_SUB_MODEL,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SMALL,
)


class ConfigFrame(ctk.CTkFrame):
    """Sidebar panel for RLM configuration."""

    def __init__(self, master, on_start_session=None, on_reset_session=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_dark"], **kwargs)

        self._on_start_session = on_start_session
        self._on_reset_session = on_reset_session
        self._config_path = Path(CONFIG_FILE).expanduser()
        self._saved_config = self._load_config()

        self._build_ui()
        self._restore_config()

    def _build_ui(self):
        # Make this frame scrollable
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=5, pady=5)
        parent = self._scroll

        # --- Custom Instructions ---
        self._section_label(parent, "Custom Instructions")
        self.custom_instructions = ctk.CTkTextbox(
            parent,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_medium"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            height=80,
        )
        self.custom_instructions.pack(fill="x", padx=5, pady=(0, 10))

        # --- Primary Model ---
        self._section_label(parent, "Primary Model")

        self._label(parent, "Backend:")
        self.backend_var = ctk.StringVar(value="openai")
        self.backend_dropdown = ctk.CTkOptionMenu(
            parent,
            variable=self.backend_var,
            values=BACKENDS,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_medium"],
            button_color=COLORS["bg_light"],
            button_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["bg_medium"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["bg_light"],
        )
        self.backend_dropdown.pack(fill="x", padx=5, pady=(0, 5))

        self._label(parent, "Model:")
        self.model_entry = self._entry(parent, DEFAULT_MODEL)

        self._label(parent, "API Key:")
        self.api_key_entry = self._entry(parent, "", show="*")

        # --- Sub-Query Model ---
        self.sub_query_var = ctk.BooleanVar(value=False)
        self.sub_query_check = ctk.CTkCheckBox(
            parent,
            text="Use different model for sub-queries",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["accent"],
            variable=self.sub_query_var,
            command=self._toggle_sub_query,
        )
        self.sub_query_check.pack(fill="x", padx=5, pady=(10, 5))

        # Sub-query fields (initially hidden)
        self.sub_frame = ctk.CTkFrame(parent, fg_color="transparent")

        self._label(self.sub_frame, "Sub-Query Backend:")
        self.sub_backend_var = ctk.StringVar(value="openai")
        self.sub_backend_dropdown = ctk.CTkOptionMenu(
            self.sub_frame,
            variable=self.sub_backend_var,
            values=BACKENDS,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_medium"],
            button_color=COLORS["bg_light"],
            button_hover_color=COLORS["border"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["bg_medium"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["bg_light"],
        )
        self.sub_backend_dropdown.pack(fill="x", padx=5, pady=(0, 5))

        self._label(self.sub_frame, "Sub-Query Model:")
        self.sub_model_entry = self._entry(self.sub_frame, DEFAULT_SUB_MODEL)

        self._label(self.sub_frame, "Sub-Query API Key:")
        self.sub_api_key_entry = self._entry(self.sub_frame, "", show="*")

        # --- Recursion & Execution ---
        self._section_label(parent, "Execution Settings")

        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", padx=5, pady=(0, 5))
        ctk.CTkLabel(
            row1, text="Max Depth:", font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text"], width=100, anchor="w",
        ).pack(side="left")
        self.max_depth_var = ctk.IntVar(value=1)
        self.max_depth_spin = ctk.CTkEntry(
            row1, font=(FONT_FAMILY, FONT_SIZE_SMALL), width=60,
            fg_color=COLORS["bg_medium"], text_color=COLORS["text"],
            border_color=COLORS["border"], textvariable=self.max_depth_var,
        )
        self.max_depth_spin.pack(side="left")

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", padx=5, pady=(0, 5))
        ctk.CTkLabel(
            row2, text="Max Iterations:", font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text"], width=100, anchor="w",
        ).pack(side="left")
        self.max_iter_var = ctk.IntVar(value=30)
        self.max_iter_spin = ctk.CTkEntry(
            row2, font=(FONT_FAMILY, FONT_SIZE_SMALL), width=60,
            fg_color=COLORS["bg_medium"], text_color=COLORS["text"],
            border_color=COLORS["border"], textvariable=self.max_iter_var,
        )
        self.max_iter_spin.pack(side="left")

        self.verbose_var = ctk.BooleanVar(value=True)
        self.verbose_check = ctk.CTkCheckBox(
            parent,
            text="Verbose output",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["accent"],
            variable=self.verbose_var,
        )
        self.verbose_check.pack(fill="x", padx=5, pady=(0, 10))

        # --- Session Controls ---
        self.start_btn = ctk.CTkButton(
            parent,
            text="Start Session",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg_color=COLORS["success"],
            hover_color="#7DB356",
            text_color=COLORS["bg_dark"],
            height=36,
            command=self._on_start_click,
        )
        self.start_btn.pack(fill="x", padx=5, pady=(5, 3))

        self.reset_btn = ctk.CTkButton(
            parent,
            text="Reset Session",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["error"],
            hover_color="#D4657A",
            text_color=COLORS["bg_dark"],
            height=30,
            command=self._on_reset_click,
            state="disabled",
        )
        self.reset_btn.pack(fill="x", padx=5, pady=(0, 5))

        # --- Status ---
        self.status_label = ctk.CTkLabel(
            parent,
            text="Status: No session",
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["muted"],
            anchor="w",
            wraplength=280,
        )
        self.status_label.pack(fill="x", padx=5, pady=(0, 5))

    def _section_label(self, parent, text: str):
        sep = ctk.CTkFrame(parent, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=5, pady=(10, 3))
        ctk.CTkLabel(
            parent,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            text_color=COLORS["secondary"],
            anchor="w",
        ).pack(fill="x", padx=5, pady=(0, 3))

    def _label(self, parent, text: str):
        ctk.CTkLabel(
            parent,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            text_color=COLORS["text"],
            anchor="w",
        ).pack(fill="x", padx=5, pady=(2, 0))

    def _entry(self, parent, default: str, show: str = "") -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            font=(FONT_FAMILY, FONT_SIZE_SMALL),
            fg_color=COLORS["bg_medium"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            placeholder_text_color=COLORS["muted"],
        )
        if show:
            entry.configure(show=show)
        if default:
            entry.insert(0, default)
        entry.pack(fill="x", padx=5, pady=(0, 5))
        return entry

    def _toggle_sub_query(self):
        if self.sub_query_var.get():
            self.sub_frame.pack(fill="x", padx=0, pady=(0, 5),
                                after=self.sub_query_check)
        else:
            self.sub_frame.pack_forget()

    def _on_start_click(self):
        self._save_config()
        if self._on_start_session:
            self._on_start_session()

    def _on_reset_click(self):
        if self._on_reset_session:
            self._on_reset_session()

    def set_session_active(self, active: bool):
        """Toggle UI state between active session and configuration mode."""
        state = "disabled" if active else "normal"
        self.start_btn.configure(state=state)
        self.reset_btn.configure(state="normal" if active else "disabled")
        self.backend_dropdown.configure(state=state)
        self.model_entry.configure(state=state)
        self.api_key_entry.configure(state=state)
        self.sub_query_check.configure(state=state)
        self.max_depth_spin.configure(state=state)
        self.max_iter_spin.configure(state=state)

    def set_status(self, text: str):
        self.status_label.configure(text=f"Status: {text}")

    # --- Config Persistence ---

    def get_config(self) -> dict:
        """Return current configuration as a dict."""
        api_key = self.api_key_entry.get().strip()
        backend = self.backend_var.get()

        # Fallback to env var if no key entered
        if not api_key:
            fallbacks = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "gemini": "GEMINI_API_KEY",
            }
            env_name = fallbacks.get(backend, f"{backend.upper()}_API_KEY")
            api_key = os.getenv(env_name, "")

        config = {
            "backend": backend,
            "model": self.model_entry.get().strip() or DEFAULT_MODEL,
            "api_key": api_key,
            "max_depth": self.max_depth_var.get(),
            "max_iterations": self.max_iter_var.get(),
            "verbose": self.verbose_var.get(),
            "custom_instructions": self.custom_instructions.get("1.0", "end-1c").strip(),
        }

        if self.sub_query_var.get():
            sub_api_key = self.sub_api_key_entry.get().strip()
            sub_backend = self.sub_backend_var.get()
            if not sub_api_key:
                fallbacks = {
                    "openai": "OPENAI_API_KEY",
                    "anthropic": "ANTHROPIC_API_KEY",
                    "gemini": "GEMINI_API_KEY",
                }
                env_name = fallbacks.get(sub_backend, f"{sub_backend.upper()}_API_KEY")
                sub_api_key = os.getenv(env_name, "")

            config["sub_query"] = {
                "backend": sub_backend,
                "model": self.sub_model_entry.get().strip() or DEFAULT_SUB_MODEL,
                "api_key": sub_api_key,
            }

        return config

    def _load_config(self) -> dict:
        try:
            if self._config_path.exists():
                return json.loads(self._config_path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _save_config(self):
        """Save API keys and settings to config file."""
        config = self._saved_config.copy()
        api_keys = config.get("api_keys", {})

        # Save primary API key
        key = self.api_key_entry.get().strip()
        if key:
            api_keys[self.backend_var.get()] = key

        # Save sub-query API key
        if self.sub_query_var.get():
            sub_key = self.sub_api_key_entry.get().strip()
            if sub_key:
                api_keys[f"sub_{self.sub_backend_var.get()}"] = sub_key

        config["api_keys"] = api_keys
        config["last_backend"] = self.backend_var.get()
        config["last_model"] = self.model_entry.get().strip()
        config["custom_instructions"] = self.custom_instructions.get("1.0", "end-1c").strip()
        config["sub_query_enabled"] = self.sub_query_var.get()
        if self.sub_query_var.get():
            config["last_sub_backend"] = self.sub_backend_var.get()
            config["last_sub_model"] = self.sub_model_entry.get().strip()

        try:
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            self._config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except Exception:
            pass

        self._saved_config = config

    def _restore_config(self):
        """Restore saved settings from config file."""
        cfg = self._saved_config
        if not cfg:
            return

        if "last_backend" in cfg:
            self.backend_var.set(cfg["last_backend"])
        if "last_model" in cfg and cfg["last_model"]:
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, cfg["last_model"])

        # Restore API keys
        api_keys = cfg.get("api_keys", {})
        backend = self.backend_var.get()
        if backend in api_keys:
            self.api_key_entry.insert(0, api_keys[backend])

        # Restore custom instructions
        if "custom_instructions" in cfg and cfg["custom_instructions"]:
            self.custom_instructions.insert("1.0", cfg["custom_instructions"])

        # Restore sub-query settings
        if cfg.get("sub_query_enabled"):
            self.sub_query_var.set(True)
            self._toggle_sub_query()
            if "last_sub_backend" in cfg:
                self.sub_backend_var.set(cfg["last_sub_backend"])
            if "last_sub_model" in cfg and cfg["last_sub_model"]:
                self.sub_model_entry.delete(0, "end")
                self.sub_model_entry.insert(0, cfg["last_sub_model"])
            sub_backend = self.sub_backend_var.get()
            sub_key_name = f"sub_{sub_backend}"
            if sub_key_name in api_keys:
                self.sub_api_key_entry.insert(0, api_keys[sub_key_name])
