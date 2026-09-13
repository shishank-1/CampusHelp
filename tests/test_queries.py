"""
CampusHelp - Phase 7: Test Queries
--------------------------------------
A set of sample questions used to manually or semi-automatically check that
the system retrieves the right source and gives a sensible answer.

This is NOT a formal unit-test suite with mocked dependencies — it runs the
real pipeline (retrieve + generate) against the real vector store, so it
requires ingest.py and embed.py to have already been run on the sample docs
(exam_rules.docx, fee_structure.txt, fee_structure.docx, exam_rules.pdf).

Usage:
    python tests/test_queries.py
"""

import sys
from pathlib import Path

# Allow running this file directly without installing the package
sys.path.append(str(Path(__file__).parent.parent / "src"))

from pipeline import ask_question


# ---------- Test cases ----------
# Each case: (question, expected_source_substring, should_be_grounded)
#
# expected_source_substring: a string we expect to appear in at least one
#   of the returned source filenames, if the system retrieves correctly.
# should_be_grounded: whether we expect the system to find relevant context
#   at all (False = we expect the fallback "I don't have this information").
TEST_CASES = [
    (
        "What is the minimum attendance required to sit for exams?",
        "exam_rules",
        True,
    ),
    (
        "How many marks are needed to pass a subject?",
        "exam_rules",
        True,
    ),
    (
        "What is the semester fee for the current year?",
        "fee_structure",
        True,
    ),
    (
        "Is there a late fee penalty for delayed payment?",
        "fee_structure",
        True,
    ),
    (
        "What is the hostel curfew time?",
        None,
        False,  # not covered in any document -> should trigger fallback
    ),
    (
        "Who is the Prime Minister of India?",
        None,
        False,  # irrelevant to campus documents -> should trigger fallback
    ),
]


# ---------- Test runner ----------
def run_tests():
    passed = 0
    failed = 0

    print(f"Running {len(TEST_CASES)} test queries...\n")
    print("=" * 70)

    for i, (question, expected_source, should_be_grounded) in enumerate(TEST_CASES, 1):
        result = ask_question(question)

        grounded_ok = (result["grounded"] == should_be_grounded)

        source_ok = True
        if expected_source is not None:
            source_ok = any(expected_source in s for s in result["sources"])

        test_passed = grounded_ok and source_ok

        status = "PASS" if test_passed else "FAIL"
        if test_passed:
            passed += 1
        else:
            failed += 1

        print(f"[{i}] {status}  \"{question}\"")
        print(f"    Answer:   {result['answer'][:150]}")
        print(f"    Sources:  {result['sources']}")
        print(f"    Grounded: {result['grounded']} (expected: {should_be_grounded})")
        if not test_passed:
            if not grounded_ok:
                print(f"    !! Grounded mismatch")
            if not source_ok:
                print(f"    !! Expected source containing '{expected_source}', got {result['sources']}")
        print("-" * 70)

    print(f"\nResults: {passed} passed, {failed} failed out of {len(TEST_CASES)}")
    return passed, failed


if __name__ == "__main__":
    run_tests()