# Capstone requirements and completion tracker

Status key: `DONE` = implemented and verified; `IN PROGRESS` = work started, not yet complete; `NOT STARTED` = still required. Do not mark an item complete without evidence.

## Submission items (all five required)

| Requirement | Status | Evidence / next action |
|---|---|---|
| Public GitHub repository link | NOT STARTED | Create a public repository and push the reviewed project; user requested public visibility. |
| Live public demo URL | NOT STARTED | Deploy Streamlit or Gradio to an allowed host and verify from a public session. |
| One-page ADR | NOT STARTED | Write after architecture choices are tested. |
| RAGAS report on 20 questions | NOT STARTED | Evaluate only after pipeline and 20 verified examples exist. |
| Cost analysis for 1K / 10K / 100K users | NOT STARTED | Verify current vendor and hosting prices, document assumptions. |

## Five project stages

| Stage / requirement | Status | Evidence / next action |
|---|---|---|
| Choose domain and define scope | DONE | `domain.md` |
| 20–50 high-quality documents | IN PROGRESS | The manifest lists 33 official IFAB sources (29 HTML, 4 PDF): 32 are marked downloaded_and_extracted and 1 base PDF is marked downloaded_and_text_extractable; the collection report records 0 failures. Deduplicate overlapping content and verify the independent-document count before claiming 20–50 documents. |
| GitHub repo named for capstone | NOT STARTED | Deferred until later by user. |
| Ingestion pipeline | IN PROGRESS | First PDF extraction exists; Arabic layout needs QA. |
| Written chunking, embedding, vector DB justifications | IN PROGRESS | Candidate choices and Arabic-specific evaluation plan are in `architecture.md`; final justifications await measured comparisons. |
| Hybrid retrieval with reranking | NOT STARTED | Implement and verify. |
| 30 golden questions | IN PROGRESS | Twenty draft questions exist in `data/eval/golden_questions_draft.json`; they need visual source checks and gold chunk IDs after chunking. Add ten more after final corpus is validated. |
| Recall@5 >= 80% | NOT STARTED | Measure; tune without changing gold labels. |
| Streamlit or Gradio interface | NOT STARTED | Arabic RTL, Amiri font, simple auth, sources visible. |
| Three real-user tests | NOT STARTED | Conduct and record actual feedback only. |
| Deployment | NOT STARTED | Deploy and test public URL. |
| Thorough README | IN PROGRESS | Initial README and proposed `architecture.md` exist; architecture choices and full operational details remain to be verified. |
| RAGAS evaluation | NOT STARTED | 20-question set and report. |
| Cost scenarios | NOT STARTED | 1K, 10K, 100K with explicit assumptions. |
| ADR | NOT STARTED | One page covering material choices/tradeoffs. |

## Current factual status

- Domain: Arabic assistant for association-football laws.
- Reference corpus edition: IFAB Laws of the Game 2026/27 Arabic.
- Source PDF: 236 pages, not encrypted, text extractable.
- Extraction output: `data/extracted/laws_pages.jsonl`, page metadata retained.
- Extraction QA reports 236/236 pages with extractable text and 113 pages flagged for visual/short-text review; inspect flagged pages before treating the Arabic PDF extraction as ingestion-ready.
- No retrieval metrics, RAGAS results, user tests, public repo, deployment, or cost figures have been completed.
- API provider/key allocation is not yet confirmed. `API_KEY_GUIDE.md` explains secret handling and low-cost testing; do not commit or share the actual key.
- User confirmed that the supervisor granted an extension; the new deadline/date is not yet recorded.
