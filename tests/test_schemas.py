"""Tests for the extraction schemas module."""

from __future__ import annotations

import pytest

from rlm_legal_docs.extraction_schemas import get_schema, list_schemas


class TestSchemas:
    def test_list_schemas(self):
        schemas = list_schemas()
        assert "general" in schemas
        assert "contract" in schemas

    def test_get_schema_general(self):
        schema = get_schema("general")
        assert "prompt_description" in schema
        assert "examples" in schema
        assert isinstance(schema["prompt_description"], str)
        assert len(schema["prompt_description"]) > 0
        assert isinstance(schema["examples"], list)
        assert len(schema["examples"]) >= 2

    def test_get_schema_contract(self):
        schema = get_schema("contract")
        assert "prompt_description" in schema
        assert "examples" in schema
        assert isinstance(schema["prompt_description"], str)
        assert len(schema["examples"]) >= 2

    def test_get_schema_default_is_general(self):
        schema = get_schema()
        general = get_schema("general")
        assert schema["prompt_description"] == general["prompt_description"]

    def test_get_schema_invalid(self):
        with pytest.raises(KeyError, match="Unknown schema"):
            get_schema("nonexistent")

    def test_examples_have_extractions(self):
        for name in list_schemas():
            schema = get_schema(name)
            for example in schema["examples"]:
                assert hasattr(example, "text")
                assert hasattr(example, "extractions")
                assert len(example.extractions) > 0

    def test_extraction_classes_are_strings(self):
        for name in list_schemas():
            schema = get_schema(name)
            for example in schema["examples"]:
                for ext in example.extractions:
                    assert isinstance(ext.extraction_class, str)
                    assert len(ext.extraction_class) > 0
