"""
Chat display frame with copyable message bubbles and input area.
"""

import tkinter as tk

import customtkinter as ctk

from rlm_legal_docs.constants import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SMALL,
    FONT_SIZE_LARGE,
)
from rlm_legal_docs.log_viewer import LogViewerWindow


class MessageBubble(ctk.CTkFrame):
    """A single chat message bubble with selectable, copyable text."""

    def __init__(self, master, sender: str, text: str, is_user: bool = True, **kwargs):
        bg = COLORS["user_bubble"] if is_user else COLORS["rlm_bubble"]
        super().__init__(master, fg_color=bg, corner_radius=10, **kwargs)

        # Sender label
        sender_color = COLORS["accent"] if is_user else COLORS["success"]
        sender_label = ctk.CTkLabel(
            self,
            text=sender,
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            text_color=sender_color,
            anchor="w",
        )
        sender_label.pack(fill="x", padx=12, pady=(8, 2))

        # Message text (selectable/copyable via CTkTextbox)
        self.textbox = ctk.CTkTextbox(
            self,
            font=(FONT_FAMILY, FONT_SIZE),
            fg_color=bg,
            text_color=COLORS["white"],
            wrap="word",
            activate_scrollbars=False,
            height=10,  # Will be auto-sized
            border_width=0,
        )
        self.textbox.insert("1.0", text)
        self.textbox.configure(state="disabled")
        self.textbox.pack(fill="x", padx=10, pady=(0, 8))

        # Auto-size height based on content
        self._text = text
        self.after(10, self._auto_resize)

        # Right-click context menu
        self._context_menu = tk.Menu(self, tearoff=0, bg=COLORS["bg_medium"],
                                      fg=COLORS["text"], activebackground=COLORS["bg_light"])
        self._context_menu.add_command(label="Copy Selection", command=self._copy_selection)
        self._context_menu.add_command(label="Copy All", command=self._copy_all)
        self.textbox.bind("<Button-3>", self._show_context_menu)

    def _auto_resize(self):
        """Resize the textbox to fit its content."""
        lines = self._text.count("\n") + 1
        # Estimate characters per line based on widget width
        widget_width = self.textbox.winfo_width()
        if widget_width < 50:
            widget_width = 500  # Fallback before layout
        char_width = FONT_SIZE * 0.6  # Approximate
        chars_per_line = max(int(widget_width / char_width), 40)

        # Count wrapped lines
        total_lines = 0
        for line in self._text.split("\n"):
            total_lines += max(1, -(-len(line) // chars_per_line))  # Ceiling division

        line_height = FONT_SIZE + 6
        new_height = max(total_lines * line_height, line_height)
        self.textbox.configure(height=new_height)

    def _show_context_menu(self, event):
        self._context_menu.post(event.x_root, event.y_root)

    def _copy_selection(self):
        try:
            self.textbox.configure(state="normal")
            selected = self.textbox.selection_get()
            self.textbox.configure(state="disabled")
            self.clipboard_clear()
            self.clipboard_append(selected)
        except tk.TclError:
            pass  # No selection

    def _copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self._text)


class ThinkingIndicator(ctk.CTkFrame):
    """Animated thinking indicator shown while waiting for RLM response."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["rlm_bubble"], corner_radius=10, **kwargs)

        self._label = ctk.CTkLabel(
            self,
            text="RLM is thinking...",
            font=(FONT_FAMILY, FONT_SIZE, "italic"),
            text_color=COLORS["warning"],
        )
        self._label.pack(padx=12, pady=10)

        self._dots = 0
        self._animate()

    def _animate(self):
        self._dots = (self._dots + 1) % 4
        dots = "." * self._dots
        self._label.configure(text=f"RLM is thinking{dots}")
        self._anim_id = self.after(400, self._animate)

    def destroy(self):
        if hasattr(self, "_anim_id"):
            self.after_cancel(self._anim_id)
        super().destroy()


class ChatFrame(ctk.CTkFrame):
    """Chat area with message history and input field."""

    def __init__(self, master, on_send=None, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_dark"], **kwargs)

        self._on_send = on_send
        self._thinking: ThinkingIndicator | None = None

        # --- Chat history (scrollable) ---
        self.chat_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg_dark"],
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Welcome message
        self._add_system_message(
            "Welcome to RLM Document Chat!\n\n"
            "1. Select documents using the sidebar\n"
            "2. Configure your model settings\n"
            "3. Click 'Start Session' to begin\n"
            "4. Ask questions about your documents"
        )

        # --- Input area ---
        input_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=10)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.input_box = ctk.CTkTextbox(
            input_frame,
            font=(FONT_FAMILY, FONT_SIZE),
            fg_color=COLORS["bg_medium"],
            text_color=COLORS["white"],
            height=60,
            wrap="word",
            border_width=0,
        )
        self.input_box.pack(fill="x", padx=(10, 80), pady=5)
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", self._on_shift_enter)

        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["accent"],
            text_color=COLORS["bg_dark"],
            width=60,
            height=40,
            command=self._send_message,
        )
        self.send_btn.place(relx=1.0, rely=0.5, anchor="e", x=-10)

        self.set_input_enabled(False)

    def _on_enter(self, event):
        """Send on Enter (without shift)."""
        self._send_message()
        return "break"  # Prevent newline insertion

    def _on_shift_enter(self, event):
        """Allow Shift+Enter for newlines."""
        return None  # Allow default behavior

    def _send_message(self):
        text = self.input_box.get("1.0", "end-1c").strip()
        if not text:
            return
        self.input_box.delete("1.0", "end")
        self.add_user_message(text)
        if self._on_send:
            self._on_send(text)

    def add_user_message(self, text: str):
        """Add a user message bubble to the chat."""
        bubble = MessageBubble(self.chat_scroll, sender="You", text=text, is_user=True)
        bubble.pack(fill="x", padx=(40, 5), pady=3, anchor="e")
        self._scroll_to_bottom()

    def add_rlm_message(self, text: str, log_file: str | None = None,
                        log_start_iter: int = 0, log_end_iter: int | None = None):
        """Add an RLM response bubble to the chat, optionally with a View Log button."""
        self._remove_thinking()
        bubble = MessageBubble(self.chat_scroll, sender="RLM", text=text, is_user=False)
        bubble.pack(fill="x", padx=(5, 40), pady=3, anchor="w")

        if log_file:
            log_btn = ctk.CTkButton(
                self.chat_scroll,
                text="View Execution Log",
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                fg_color="transparent",
                hover_color=COLORS["bg_light"],
                text_color=COLORS["accent"],
                anchor="w",
                width=140,
                height=24,
                command=lambda lf=log_file, si=log_start_iter, ei=log_end_iter:
                    self._open_log_viewer(lf, si, ei),
            )
            log_btn.pack(padx=(10, 40), pady=(0, 4), anchor="w")

        self._scroll_to_bottom()

    def _open_log_viewer(self, log_file: str, start_iter: int, end_iter: int | None):
        """Open the log viewer window for the given log file."""
        LogViewerWindow(self, log_file, start_iter, end_iter)

    def add_error_message(self, text: str):
        """Add an error message to the chat."""
        self._remove_thinking()
        bubble = MessageBubble(self.chat_scroll, sender="Error", text=text, is_user=False)
        # Override colors for error
        bubble.configure(fg_color="#2D1B1E")
        bubble.textbox.configure(fg_color="#2D1B1E", text_color=COLORS["error"])
        bubble.pack(fill="x", padx=(5, 40), pady=3, anchor="w")
        self._scroll_to_bottom()

    def _add_system_message(self, text: str):
        """Add a system/info message."""
        label = ctk.CTkLabel(
            self.chat_scroll,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE),
            text_color=COLORS["muted"],
            justify="left",
            anchor="w",
            wraplength=500,
        )
        label.pack(fill="x", padx=20, pady=20)

    def show_thinking(self):
        """Show the thinking indicator."""
        self._remove_thinking()
        self._thinking = ThinkingIndicator(self.chat_scroll)
        self._thinking.pack(fill="x", padx=(5, 40), pady=3, anchor="w")
        self._scroll_to_bottom()

    def _remove_thinking(self):
        """Remove the thinking indicator if present."""
        if self._thinking is not None:
            self._thinking.destroy()
            self._thinking = None

    def clear_chat(self):
        """Clear all messages from chat."""
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()

    def set_input_enabled(self, enabled: bool):
        """Enable or disable the input area."""
        if enabled:
            self.input_box.configure(state="normal")
            self.send_btn.configure(state="normal")
        else:
            self.input_box.configure(state="disabled")
            self.send_btn.configure(state="disabled")

    def _scroll_to_bottom(self):
        """Scroll the chat to the bottom."""
        self.chat_scroll.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
