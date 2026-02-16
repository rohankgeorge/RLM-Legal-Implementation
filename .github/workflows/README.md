# GitHub Actions Workflows

This directory contains automated workflows for the RLM Legal Document Tool project.

## Workflows

### 1. Style (`style.yml`)
**Purpose**: Code style checking using ruff.

**Triggers**:
- Pull requests (opened, synchronized, reopened)
- Pushes to `main` branch

**What it does**:
- Runs ruff for linting and formatting checks
- Uses configuration from `pyproject.toml`

### 2. Test (`test.yml`)
**Purpose**: Run tests.

**Triggers**:
- Pull requests
- Pushes to `main` branch
- Pushes to `claude/*` branches

**What it does**:
- Runs tests on multiple Python versions (3.11, 3.12)
- Tests legal document tool functionality

## Setting Up

### Branch Protection
It's recommended to set up branch protection rules for your main branch:
1. Go to Settings → Branches
2. Add a rule for your main branch
3. Enable "Require status checks to pass before merging"
4. Select the CI jobs you want to require (e.g., `style`, `test`)

## Running Tests Locally

To run tests locally the same way they run in CI:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Running Style Checks Locally

```bash
# Run linting
make lint

# Run formatting
make format

# Run both
make check
```

Or directly with ruff:

```bash
# Run linting
ruff check .

# Run formatting check
ruff format --check .

# Auto-fix linting issues
ruff check --fix .

# Auto-format code
ruff format .
```

## Customization

### Adding New Python Versions
Edit the `matrix.python-version` in `test.yml` to test on additional Python versions.

### Changing Trigger Conditions
Modify the `on:` section in the workflow files to change when workflows run.

### Adding More Checks
You can extend the workflows to include:
- Type checking with mypy
- Security scanning
- Package building and publishing (when ready for PyPI)
