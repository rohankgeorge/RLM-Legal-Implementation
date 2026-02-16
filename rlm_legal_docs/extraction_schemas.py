"""Predefined legal extraction schemas for LangExtract.

Each schema provides a prompt description and few-shot examples
for extracting structured entities from legal documents.
"""

from __future__ import annotations

import langextract as lx

# ---------------------------------------------------------------------------
# Extraction class constants
# ---------------------------------------------------------------------------

CLASSES_GENERAL = [
    "date",
    "monetary_amount",
    "party",
    "organization",
    "legal_reference",
    "obligation",
    "deadline",
    "condition",
]

CLASSES_CONTRACT = [
    "party",
    "effective_date",
    "expiry_date",
    "governing_law",
    "indemnity_cap",
    "liability_limitation",
    "confidentiality_period",
    "notice_period",
    "renewal_terms",
    "assignment_restriction",
]

# ---------------------------------------------------------------------------
# Schema definitions
# ---------------------------------------------------------------------------

_GENERAL_SCHEMA: dict | None = None
_CONTRACT_SCHEMA: dict | None = None


def _build_general_schema() -> dict:
    """General catch-all schema for any legal document."""
    prompt_description = (
        "Extract all dates, monetary amounts, party names, organization names, "
        "legal references (statutes, case names, contract names), obligations, "
        "deadlines, and conditions from this legal document. "
        "Each extraction should include the exact text from the source."
    )

    examples = [
        lx.data.ExampleData(
            text=(
                "This Agreement is entered into as of January 15, 2024, "
                "by and between Acme Corporation and Beta Industries LLC. "
                "The total consideration shall be USD 2,500,000. "
                "All disputes shall be governed by the laws of the State of Delaware."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="date",
                    extraction_text="January 15, 2024",
                    attributes={"context": "agreement date"},
                ),
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="Acme Corporation",
                    attributes={"role": "first party"},
                ),
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="Beta Industries LLC",
                    attributes={"role": "second party"},
                ),
                lx.data.Extraction(
                    extraction_class="monetary_amount",
                    extraction_text="USD 2,500,000",
                    attributes={"context": "total consideration"},
                ),
                lx.data.Extraction(
                    extraction_class="legal_reference",
                    extraction_text="laws of the State of Delaware",
                    attributes={"type": "governing law"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Pursuant to Section 12(b) of the Securities Exchange Act of 1934, "
                "the Borrower shall repay the outstanding principal of EUR 1,000,000 "
                "no later than March 31, 2025. Failure to comply shall constitute "
                "an event of default under Clause 8.2."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="legal_reference",
                    extraction_text="Section 12(b) of the Securities Exchange Act of 1934",
                    attributes={"type": "statute"},
                ),
                lx.data.Extraction(
                    extraction_class="obligation",
                    extraction_text="the Borrower shall repay the outstanding principal",
                    attributes={"obligor": "Borrower"},
                ),
                lx.data.Extraction(
                    extraction_class="monetary_amount",
                    extraction_text="EUR 1,000,000",
                    attributes={"context": "outstanding principal"},
                ),
                lx.data.Extraction(
                    extraction_class="deadline",
                    extraction_text="no later than March 31, 2025",
                    attributes={"context": "repayment deadline"},
                ),
                lx.data.Extraction(
                    extraction_class="condition",
                    extraction_text="Failure to comply shall constitute an event of default",
                    attributes={"trigger": "non-repayment"},
                ),
                lx.data.Extraction(
                    extraction_class="legal_reference",
                    extraction_text="Clause 8.2",
                    attributes={"type": "contract clause"},
                ),
            ],
        ),
    ]

    return {"prompt_description": prompt_description, "examples": examples}


def _build_contract_schema() -> dict:
    """Schema tailored for contracts and agreements."""
    prompt_description = (
        "Extract key contract terms: parties and their roles, effective date, "
        "expiry or termination date, governing law, indemnity cap, liability "
        "limitation, confidentiality period, notice period, renewal terms, "
        "and assignment restrictions. Extract the exact text from the source."
    )

    examples = [
        lx.data.ExampleData(
            text=(
                "SERVICE AGREEMENT dated 1 April 2024 between GlobalTech Inc. "
                '("Provider") and Meridian Holdings Ltd ("Client"). '
                "This Agreement shall remain in force until 31 March 2027 "
                "unless terminated earlier pursuant to Clause 14. "
                "The Provider's total aggregate liability shall not exceed "
                "the fees paid in the preceding 12-month period. "
                "This Agreement shall be governed by English law."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="GlobalTech Inc.",
                    attributes={"role": "Provider"},
                ),
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="Meridian Holdings Ltd",
                    attributes={"role": "Client"},
                ),
                lx.data.Extraction(
                    extraction_class="effective_date",
                    extraction_text="1 April 2024",
                    attributes={},
                ),
                lx.data.Extraction(
                    extraction_class="expiry_date",
                    extraction_text="31 March 2027",
                    attributes={"condition": "unless terminated earlier pursuant to Clause 14"},
                ),
                lx.data.Extraction(
                    extraction_class="liability_limitation",
                    extraction_text="total aggregate liability shall not exceed the fees paid in the preceding 12-month period",
                    attributes={"party": "Provider"},
                ),
                lx.data.Extraction(
                    extraction_class="governing_law",
                    extraction_text="English law",
                    attributes={},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Either party may assign this Agreement with the prior written "
                "consent of the other party, such consent not to be unreasonably "
                "withheld. Confidential Information shall be protected for a "
                "period of five (5) years following termination. Any notice "
                "required shall be delivered in writing with 30 days advance notice."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="assignment_restriction",
                    extraction_text="may assign this Agreement with the prior written consent of the other party",
                    attributes={"condition": "consent not to be unreasonably withheld"},
                ),
                lx.data.Extraction(
                    extraction_class="confidentiality_period",
                    extraction_text="five (5) years following termination",
                    attributes={},
                ),
                lx.data.Extraction(
                    extraction_class="notice_period",
                    extraction_text="30 days advance notice",
                    attributes={"method": "in writing"},
                ),
            ],
        ),
    ]

    return {"prompt_description": prompt_description, "examples": examples}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

SCHEMAS: dict[str, dict] = {}


def _ensure_schemas_loaded():
    """Lazily build schemas on first access."""
    if not SCHEMAS:
        SCHEMAS["general"] = _build_general_schema()
        SCHEMAS["contract"] = _build_contract_schema()


def get_schema(name: str = "general") -> dict:
    """Return a schema dict with 'prompt_description' and 'examples' keys.

    Raises KeyError if the schema name is unknown.
    """
    _ensure_schemas_loaded()
    if name not in SCHEMAS:
        raise KeyError(f"Unknown schema: {name!r}. Available: {list(SCHEMAS.keys())}")
    return SCHEMAS[name]


def list_schemas() -> list[str]:
    """Return available schema names."""
    _ensure_schemas_loaded()
    return list(SCHEMAS.keys())
