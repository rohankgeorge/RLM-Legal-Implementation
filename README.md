# RLM Legal Document Query Tool

Desktop GUI and CLI for querying legal documents using Recursive Language Models (RLM). Supports .docx, .pdf, and .txt files with intelligent recursive query processing.

## Features

- **Desktop GUI** with chatbot interface for interactive document analysis
- **CLI tool** for batch processing and automation
- **Multi-document ingestion** - load and query multiple documents simultaneously
- **Format support** - .docx, .pdf, and .txt files
- **Multiple LLM backends** - OpenAI, Anthropic, OpenRouter, Portkey, and more
- **Recursive query processing** - leverages RLM for handling complex multi-step queries

## Quick Start

### Installation

```bash
pip install rlm-legal-docs
```

Or install from source:

```bash
git clone https://github.com/rohankgeorge/RLM-Legal-Implementation.git
cd RLM-Legal-Implementation
pip install -e .
```

### GUI Usage

Launch the desktop application:

```bash
rlm-legal-gui
```

**Using the GUI:**

1. **Select documents**: Click "Select Files" or "Select Folder" to load .docx, .pdf, or .txt files
2. **Configure LLM**: Choose your LLM provider (OpenAI, Anthropic, etc.) and enter your API key
3. **Ask questions**: Type questions about your documents in the chat interface
4. **View results**: RLM will recursively process your query and display the results

### CLI Usage

```bash
# Interactive mode
rlm-legal-query --folder ./documents --interactive

# Single query
rlm-legal-query --folder ./documents --query "What are the key contractual obligations?"
```

## Requirements

- Python 3.11 or higher
- API key for supported LLM provider (OpenAI, Anthropic, etc.)

## Documentation

- **GUI Guide**: See [rlm_legal_docs/README.md](rlm_legal_docs/README.md) for detailed GUI documentation
- **Installation**: Standard pip installation or build from source
- **Configuration**: API keys can be set via environment variables or through the GUI

## Technology

This tool is built on the [Recursive Language Models (RLM) library](https://github.com/alexzhang13/rlm) by Alex Zhang. RLM enables language models to programmatically examine, decompose, and recursively process contexts of near-infinite length.

**What is RLM?**

Recursive Language Models (RLMs) are a task-agnostic inference paradigm that allows language models to handle near-infinite length contexts by enabling the LM to programmatically examine, decompose, and recursively call itself over its input. This makes RLM particularly well-suited for legal document analysis where documents can be lengthy and complex.

### Learn More About RLM

- **Paper**: [Recursive Language Models (arXiv:2512.24601)](https://arxiv.org/abs/2512.24601)
- **Documentation**: [alexzhang13.github.io/rlm](https://alexzhang13.github.io/rlm/)
- **Blog Post**: [RLM Introduction](https://alexzhang13.github.io/blog/2025/rlm/)

## Attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) for full attribution and citation information.

## License

MIT License - See [LICENSE](LICENSE) for details.

This project uses the RLM library (Copyright 2025 Alex Zhang) as a dependency under the MIT License.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Development

### Setup

```bash
git clone https://github.com/rohankgeorge/RLM-Legal-Implementation.git
cd RLM-Legal-Implementation
make install-dev
```

### Run Tests

```bash
make test
```

### Run Linting

```bash
make lint
```

### Build Package

```bash
python -m build
```
