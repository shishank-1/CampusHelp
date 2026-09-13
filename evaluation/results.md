# CampusHelp — Evaluation Results

## 1. Test Setup

- **Test file:** `tests/test_queries.py`
- **Sample documents used:** `exam_rules.docx`, `exam_rules.pdf`, `fee_structure.txt`, `fee_structure.docx`
- **Embedding model:** `all-MiniLM-L6-v2` (sentence-transformers)
- **LLM:** Claude (claude-sonnet-4-6)
- **Similarity threshold:** 0.35
- **Date of this run:** <!-- fill in when you actually run it -->
- **Total test queries:** 6

## 2. Summary

| Metric | Result |
|---|---|
| Total queries tested | 6 |
| Correctly grounded (found right source) | <!-- e.g. 5 / 6 --> |
| Correctly fell back (no hallucination on out-of-scope Qs) | <!-- e.g. 2 / 2 --> |
| Overall pass rate | <!-- e.g. 83% (5/6) --> |

## 3. Detailed Results

| # | Question | Expected Source | Actual Source(s) | Grounded? | Pass/Fail |
|---|---|---|---|---|---|
| 1 | What is the minimum attendance required to sit for exams? | exam_rules | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |
| 2 | How many marks are needed to pass a subject? | exam_rules | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |
| 3 | What is the semester fee for the current year? | fee_structure | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |
| 4 | Is there a late fee penalty for delayed payment? | fee_structure | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |
| 5 | What is the hostel curfew time? | (none — fallback expected) | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |
| 6 | Who is the Prime Minister of India? | (none — fallback expected) | <!-- fill in --> | <!-- fill in --> | <!-- fill in --> |

## 4. Example Q&A Pairs (Worked Examples)

### Example 1 — Correctly grounded answer
**Q:** What is the minimum attendance required to sit for exams?
**A:** <!-- paste actual LLM output here -->
**Source:** exam_rules.docx
**Notes:** <!-- e.g. "Matched on first try, high similarity score (~0.8)" -->

### Example 2 — Correctly triggered fallback (no hallucination)
**Q:** What is the hostel curfew time?
**A:** I don't have this information in the available documents. Please check with the administration office.
**Source:** none
**Notes:** No chunk in the knowledge base met the similarity threshold, so the system skipped the LLM call entirely and returned the fallback — exactly the intended behavior.

## 5. Known Limitations / Failure Cases

<!-- Fill this in honestly once you've run real tests. Things to look for: -->
<!-- - Does it ever retrieve the WRONG source with high confidence? -->
<!-- - Does chunking ever split a fact across two chunks so neither alone answers it? -->
<!-- - Does the similarity threshold need tuning (too strict = false fallbacks, too loose = weak matches get through)? -->

## 6. Next Steps

- [ ] Tune `MIN_SIMILARITY` threshold based on false-positive/false-negative rate
- [ ] Add more test queries covering edge cases (ambiguous questions, multi-part questions)
- [ ] Consider chunk size/overlap tuning if answers are cut off mid-fact