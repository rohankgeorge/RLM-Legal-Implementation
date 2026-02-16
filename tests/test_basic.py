"""Basic tests for RLM Legal Document Tools."""

import pytest


def test_import():
    """Test that package imports successfully."""
    import rlm_legal_docs

    assert hasattr(rlm_legal_docs, "__version__")
    assert rlm_legal_docs.__version__ == "0.1.0"


def test_rlm_dependency():
    """Test that RLM is available as dependency."""
    from rlm import RLM

    assert RLM is not None


def test_cli_entry_points():
    """Test that CLI entry points exist."""
    from rlm_legal_docs import cli

    assert hasattr(cli, "run_gui")
    assert hasattr(cli, "run_query")
    assert callable(cli.run_gui)
    assert callable(cli.run_query)


def test_package_modules():
    """Test that main package modules are importable."""
    # Test constants (doesn't require tkinter)
    from rlm_legal_docs import constants

    assert constants is not None
    assert hasattr(constants, "BACKENDS")

    # Try importing GUI modules, but skip if tkinter not available
    try:
        from rlm_legal_docs import app, chat_frame, config_frame, file_frame, workers

        assert app is not None
        assert chat_frame is not None
        assert config_frame is not None
        assert file_frame is not None
        assert workers is not None
    except ModuleNotFoundError as e:
        if "tkinter" in str(e):
            pytest.skip("tkinter not available (headless environment)")
        else:
            raise
