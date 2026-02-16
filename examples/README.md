# Examples

This directory contains example scripts demonstrating how to use the RLM Legal Document Query Tool.

## Simple Query Example

**File**: `simple_query.py`

Demonstrates basic usage of the RLM library to query a legal document programmatically.

### Prerequisites

- Python 3.11+
- OpenAI API key set as environment variable

### Usage

```bash
# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Run the example
python examples/simple_query.py
```

### What it does

- Creates an RLM instance with the OpenAI backend
- Loads a sample employment agreement
- Queries the document for main terms
- Displays the analysis results

## Adding Your Own Examples

When creating new examples:

1. Add a descriptive docstring explaining the example's purpose
2. Include error handling for missing API keys
3. Use clear variable names and comments
4. Add the example to this README

## GUI and CLI Usage

For interactive usage, see:
- **GUI**: Run `rlm-legal-gui` for the desktop application
- **CLI**: See main README.md for command-line usage
