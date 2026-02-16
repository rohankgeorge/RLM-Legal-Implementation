# Contributing to RLM Legal Document Tool

Thank you for your interest in contributing!

## Development Setup

```bash
git clone https://github.com/rohankgeorge/RLM-Legal-Implementation.git
cd RLM-Legal-Implementation
uv sync --group dev --group test
```

Or with pip:

```bash
pip install -e ".[dev]"
```

## Code Style

- Follow PEP 8 guidelines
- Use ruff for linting and formatting
- Run `make check` before submitting PRs
- Add type hints where appropriate
- Keep functions focused and well-documented

## Testing

```bash
make test
```

Add tests for new features in the `tests/` directory.

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with clear commit messages following [Conventional Commits](https://www.conventionalcommits.org/)
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for test additions/changes
4. Add tests if applicable
5. Run `make check` to verify code quality
6. Submit a pull request

## Project Scope

This project focuses on legal document analysis tools built on the RLM library.

### In Scope

- GUI improvements and new features
- CLI enhancements
- Document format support (additional file types)
- Legal document-specific functionality
- Integration with additional LLM providers
- Performance improvements
- Bug fixes
- Documentation improvements

### Out of Scope

- Issues with the underlying RLM library (report at [alexzhang13/rlm](https://github.com/alexzhang13/rlm))
- Core RLM execution logic modifications (contribute upstream)
- General-purpose document analysis (focus on legal documents)

## Development Guidelines

### Adding New Features

- Discuss major features in an issue before implementing
- Keep changes focused and avoid scope creep
- Update documentation alongside code changes
- Add examples if introducing new functionality

### Bug Fixes

- Include a test that reproduces the bug
- Reference the issue number in your commit message
- Verify the fix doesn't break existing functionality

### Documentation

- Update README.md if adding user-facing features
- Update rlm_legal_docs/README.md for GUI changes
- Add docstrings to new functions and classes
- Include examples for complex features

## Code Quality

Before submitting a PR, ensure:

```bash
# Lint code
make lint

# Format code
make format

# Run tests
make test

# Or run all checks
make check
```

## Questions?

- Open an issue for bug reports or feature requests
- Start a discussion for general questions
- Review existing issues before opening a new one

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
