# RLM Document Chat

Desktop GUI for ingesting documents and querying them with the Recursive Learning Model (RLM). Supports `.docx`, `.pdf`, and `.txt` files with a chatbot-style interface.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

All dependencies are included in the project's `pyproject.toml`. From the repository root:

```bash
uv sync
```

## Running the App

```bash
uv run python docx_rlm_gui.py
```

## Quick Start

1. **Select documents** — Click **Select Folder** to load all supported files from a directory, or **Select Files** to pick individual files. Supported formats: `.docx`, `.pdf`, `.txt`.
2. **Configure your model** — In the left sidebar, choose a backend, enter a model name, and provide an API key (or set it via environment variable).
3. **Optional settings** — Add custom instructions, enable a sub-query model for recursive calls, or adjust max depth and iterations.
4. **Start the session** — Click **Start Session**. The app ingests the checked files and creates an RLM instance.
5. **Ask questions** — Type a question in the input box at the bottom and press **Enter** to send.
6. **Copy responses** — Click and drag to select text, then **Ctrl+C** to copy. Or right-click a message and choose **Copy All**.
7. **Reset** — Click **Reset Session** to clear the chat and load different documents or change settings.

## API Key Configuration

You can provide API keys in two ways:

- **Environment variables** — Set the appropriate variable before launching:
  ```bash
  set OPENAI_API_KEY=sk-...          # Windows
  export OPENAI_API_KEY=sk-...       # macOS/Linux
  ```
- **In the GUI** — Enter the key directly in the API Key field in the sidebar.

Keys entered in the GUI are saved to `~/.rlm_gui_config.json` so you don't need to re-enter them each session. Keys are stored per backend name.

### Common Environment Variable Names

| Backend       | Environment Variable      |
|---------------|---------------------------|
| openai        | `OPENAI_API_KEY`          |
| anthropic     | `ANTHROPIC_API_KEY`       |
| gemini        | `GEMINI_API_KEY`          |
| azure_openai  | `AZURE_OPENAI_API_KEY`    |
| litellm       | `LITELLM_API_KEY`         |
| portkey       | `PORTKEY_API_KEY`         |
| openrouter    | `OPENROUTER_API_KEY`      |
| vercel        | `VERCEL_API_KEY`          |
| vllm          | `VLLM_API_KEY`            |

## Supported Backends

`openai`, `anthropic`, `gemini`, `azure_openai`, `litellm`, `portkey`, `openrouter`, `vercel`, `vllm`

## Keyboard Shortcuts

| Shortcut          | Action                        |
|-------------------|-------------------------------|
| Enter             | Send message                  |
| Shift+Enter       | Insert newline in input       |
| Ctrl+C            | Copy selected text            |
| Right-click       | Context menu (Copy / Copy All)|

## Building a Standalone Executable

You can package the app as a single `.exe` using PyInstaller:

```bash
uv add --dev pyinstaller
uv run pyinstaller --onefile --windowed --name "RLM-DocChat" docx_rlm_gui.py
```

The resulting executable will be in the `dist/` folder.

> **Note:** If the app fails to find customtkinter assets at runtime, you may need to add them explicitly:
> ```bash
> uv run pyinstaller --onefile --windowed --name "RLM-DocChat" \
>     --add-data "<path-to-customtkinter>;customtkinter" \
>     docx_rlm_gui.py
> ```
> Find the customtkinter path with: `python -c "import customtkinter; print(customtkinter.__path__[0])"`
