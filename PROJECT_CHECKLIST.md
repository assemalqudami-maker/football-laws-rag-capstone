# Capstone requirements and completion tracker

Status key: `DONE` = implemented and verified; `IN PROGRESS` = work started, not yet complete; `NOT STARTED` = still required. Do not mark an item complete without evidence.

## Submission items (all five required)

| Requirement | Status | Evidence / next action |
|---|---|---|
| Public GitHub repository link | DONE | [Public repository](https://github.com/assemalqudami-maker/football-laws-rag-capstone); project files are on `main`. |
| Live public demo URL | NOT STARTED | Deploy Streamlit or Gradio to an allowed host and verify from a public session. |
| One-page ADR | NOT STARTED | Write after architecture choices are tested. |
| RAGAS report on 20 questions | NOT STARTED | Evaluate only after pipeline and 20 verified examples exist. |
| Cost analysis for 1K / 10K / 100K users | NOT STARTED | Verify current vendor and hosting prices, document assumptions. |

## Five project stages

| Stage / requirement | Status | Evidence / next action |
|---|---|---|
| Choose domain and define scope | DONE | `domain.md` |
| 20–50 high-quality documents | IN PROGRESS | The manifest has 33 extracted source records (29 HTML, 4 PDF), zero failures, and 32 document identities after merging the Arabic/English law-changes translation pair. The 17 distinct law-topic URLs each contain an FAQ marker. See `data/eval/corpus_audit.md` for the counting rule and overlap results; visual review of flagged Arabic lawbook pages remains incomplete. |
| GitHub repo named for capstone | DONE | Public repository `assemalqudami-maker/football-laws-rag-capstone`. |
| Ingestion pipeline | IN PROGRESS | Corpus audit and page-preserving chunk builder are implemented; 597 baseline chunks generated locally. Embeddings and vector store are still pending. |
| Written chunking, embedding, vector DB justifications | IN PROGRESS | Candidate choices and Arabic-specific evaluation plan are in `architecture.md`; final justifications await measured comparisons. |
| Hybrid retrieval with reranking | IN PROGRESS | API-free BM25 baseline and reproducible evaluator exist; dense retrieval, fusion, and reranker are pending. |
| 30 golden questions | IN PROGRESS | Thirty draft questions have source-checked expected answers and manually linked supporting chunk IDs. Arabic book claims were checked on rendered pages; protocol answers were checked against official IFAB text. Independent review is pending, so the set remains a draft. |
| Recall@5 >= 80% | IN PROGRESS | Arabic-only BM25 baseline is 14/30 (46.7%); see `data/eval/bm25_recall_report.json`. Compare multilingual dense/hybrid retrieval on unchanged labels. |
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
- `scripts/audit_corpus.py` generates `data/eval/corpus_audit.json`; 17/17 law-specific webpages contain FAQ markers and no exact whole-document duplicate was found. Five-token overlap is reported for review, not automatically removed.
- Extraction QA reports 236/236 pages with extractable text and 113 pages originally flagged for visual/short-text review; 14 pages now have targeted visual checks, with 103 flagged pages remaining. Visual comparison and targeted content review are documented in `data/eval/pdf_extraction_review.md` and `data/eval/pdf_manual_review.json`; full-document QA is still incomplete.
- The baseline chunk builder produces 597 chunks (median 325 whitespace-delimited words, max 360, overlap 55). It excludes PDF front matter pages 1–8, flags 57 chunks requiring source review, and reports PDF page 42 as empty. Generated chunk JSONL is local and ignored by Git; the script and build report are tracked.
- The BM25 baseline is not a completed hybrid retriever. Its draft-set Recall@5 is 46.7%; no RAGAS results, user tests, deployment, or cost figures have been completed.
- API provider/key allocation is not yet confirmed. `API_KEY_GUIDE.md` explains secret handling and low-cost testing; do not commit or share the actual key.
