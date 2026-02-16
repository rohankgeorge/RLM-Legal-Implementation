"""
Simple example of using RLM Legal Document tools programmatically.

This example demonstrates how to use the RLM library to query a legal document.
"""

import os

from rlm import RLM


def main():
    """Run a simple query on a legal document."""
    # Set up RLM with OpenAI backend
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("\nPlease set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'  # Linux/Mac")
        print("  set OPENAI_API_KEY=your-api-key-here       # Windows")
        return

    # Create RLM instance
    rlm = RLM(
        backend="openai",
        model="gpt-4o",
        api_key=api_key,
    )

    # Example legal document text
    document_text = """
    EMPLOYMENT AGREEMENT

    This Employment Agreement ("Agreement") is entered into as of January 1, 2026,
    between Tech Corp ("Employer") and John Smith ("Employee").

    1. POSITION AND DUTIES
    Employee shall serve as Senior Software Engineer and shall perform all duties
    as assigned by the Employer.

    2. COMPENSATION
    Employer shall pay Employee a base salary of $150,000 per year, payable in
    accordance with Employer's standard payroll practices.

    3. BENEFITS
    Employee shall be entitled to participate in all employee benefit plans
    maintained by Employer, including health insurance and 401(k).

    4. TERM
    Employment shall commence on January 1, 2026, and continue until terminated
    by either party with 30 days written notice.

    5. CONFIDENTIALITY
    Employee agrees to maintain confidentiality of all proprietary information
    and trade secrets of the Employer during and after employment.
    """

    # Create query prompt
    prompt = f"""
    Document:
    {document_text}

    Question: What are the main terms of this employment agreement?

    Please analyze the document and provide a summary of the key terms.
    """

    # Execute query
    print("Querying legal document with RLM...")
    print("-" * 60)
    response = rlm.execute(prompt)
    print("\nResponse:")
    print(response)


if __name__ == "__main__":
    main()
