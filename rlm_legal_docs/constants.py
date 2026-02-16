"""
Tokyo Night color theme and GUI constants for the RLM Document Chat application.
Colors reused from rlm/logger/verbose.py.
"""

# Tokyo Night Color Theme
COLORS = {
    "primary": "#7AA2F7",  # Soft blue - headers, titles
    "secondary": "#BB9AF7",  # Soft purple - emphasis
    "success": "#9ECE6A",  # Soft green - success
    "warning": "#E0AF68",  # Soft amber - warnings
    "error": "#F7768E",  # Soft red/pink - errors
    "text": "#A9B1D6",  # Soft gray-blue - regular text
    "muted": "#565F89",  # Muted gray - less important
    "accent": "#7DCFFF",  # Bright cyan - accents
    "bg_dark": "#1A1B26",  # Dark background
    "bg_medium": "#24283B",  # Medium background (code/cards)
    "bg_light": "#2F3348",  # Lighter background (hover/active)
    "border": "#3B4261",  # Border color
    "white": "#C0CAF5",  # Light text
    "user_bubble": "#292E42",  # User message background
    "rlm_bubble": "#1E2030",  # RLM message background
}

# Font configuration
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 13
FONT_SIZE_SMALL = 11
FONT_SIZE_LARGE = 15

# Layout
SIDEBAR_WIDTH = 320
CHAT_INPUT_HEIGHT = 80
STATUS_BAR_HEIGHT = 30

# Backend options
BACKENDS = [
    "openai",
    "anthropic",
    "gemini",
    "azure_openai",
    "litellm",
    "portkey",
    "openrouter",
    "vercel",
    "vllm",
]

# Default models
DEFAULT_MODEL = "gpt-4o"
DEFAULT_SUB_MODEL = "gpt-4o-mini"

# Supported file extensions
SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt"}
FILE_TYPE_FILTERS = [
    ("Supported Files", "*.docx *.pdf *.txt"),
    ("Word Documents", "*.docx"),
    ("PDF Files", "*.pdf"),
    ("Text Files", "*.txt"),
]

# Config file path
CONFIG_FILE = "~/.rlm_gui_config.json"

# Worker polling interval (ms)
POLL_INTERVAL_MS = 100
