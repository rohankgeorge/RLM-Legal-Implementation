"""Tests for the system prompt module."""

from __future__ import annotations

from rlm_legal_docs.prompts import build_system_prompt


class TestBuildSystemPrompt:
    def test_with_extraction_enabled(self):
        prompt = build_system_prompt(
            extraction_enabled=True,
            custom_instructions=None,
            base_prompt="BASE",
        )
        assert "EXTRACTION INDEX" in prompt
        assert "CITATION REQUIREMENTS" in prompt
        assert "BASE" in prompt

    def test_without_extraction(self):
        prompt = build_system_prompt(
            extraction_enabled=False,
            custom_instructions=None,
            base_prompt="BASE",
        )
        assert "EXTRACTION INDEX" not in prompt
        assert prompt == "BASE"

    def test_with_custom_instructions(self):
        prompt = build_system_prompt(
            extraction_enabled=True,
            custom_instructions="Focus on contract law.",
            base_prompt="BASE",
        )
        assert "Focus on contract law." in prompt
        assert "EXTRACTION INDEX" in prompt
        assert "BASE" in prompt

    def test_ordering(self):
        prompt = build_system_prompt(
            extraction_enabled=True,
            custom_instructions="CUSTOM",
            base_prompt="BASE",
        )
        # Extraction prompt should come first
        extract_pos = prompt.index("CONTEXT STRUCTURE")
        custom_pos = prompt.index("CUSTOM")
        base_pos = prompt.index("BASE")
        assert extract_pos < custom_pos < base_pos

    def test_no_extraction_with_custom(self):
        prompt = build_system_prompt(
            extraction_enabled=False,
            custom_instructions="CUSTOM",
            base_prompt="BASE",
        )
        assert "CUSTOM" in prompt
        assert "BASE" in prompt
        assert "EXTRACTION INDEX" not in prompt

    def test_empty_base_prompt(self):
        prompt = build_system_prompt(
            extraction_enabled=True,
            custom_instructions=None,
            base_prompt="",
        )
        assert "EXTRACTION INDEX" in prompt
