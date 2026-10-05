#!/usr/bin/env python3
"""Evaluate a retrieval run against manually linked gold chunk IDs.

This API-free script measures Recall@k for the current BM25 baseline. It does
not score answer generation, and it does not promote draft questions to a
final gold set.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data" / "eval" / "golden_questions_draft.json"
CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_REPORT = ROOT / "data" / "eval" / "bm25_recall_report.json"


def load_retriever():
    spec = importlib.util.spec_from_file_location(
        "retrieve_bm25", ROOT / "scripts" / "retrieve_bm25.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load scripts/retrieve_bm25.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--include-review-required", action="store_true")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be positive")

    question_set = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    questions = question_set.get("questions", [])
    if not questions:
        raise ValueError("No questions found in evaluation draft")
    for question in questions:
        if not question.get("gold_chunk_ids"):
            raise ValueError(f"Missing gold_chunk_ids for {question.get('id')}")

    retriever = load_retriever()
    chunks = retriever.load_chunks(CHUNKS, args.include_review_required)
    chunk_ids = {chunk["chunk_id"] for chunk in chunks}
    results = []
    hits = 0
    for question in questions:
        gold_ids = set(question["gold_chunk_ids"])
        unavailable = sorted(gold_ids - chunk_ids)
        if unavailable:
            raise ValueError(
                f"Gold chunks for {question['id']} are excluded or absent: {unavailable}"
            )
        retrieved = retriever.rank_bm25(chunks, question["question"], k=args.top_k)
        ranked_ids = [item["chunk_id"] for item in retrieved]
        found_ids = [chunk_id for chunk_id in ranked_ids if chunk_id in gold_ids]
        hit = bool(found_ids)
        hits += int(hit)
        results.append(
            {
                "question_id": question["id"],
                "query": question["question"],
                "gold_chunk_ids": sorted(gold_ids),
                "retrieved_chunk_ids": ranked_ids,
                "retrieved_gold_chunk_ids": found_ids,
                "hit": hit,
            }
        )

    report = {
        "retriever": "BM25 lexical baseline",
        "query_language": "Arabic question text as stored; no translation or query expansion",
        "top_k": args.top_k,
        "candidate_chunk_count": len(chunks),
        "review_required_chunks_included": args.include_review_required,
        "question_set_status": question_set.get("status"),
        "gold_question_count": len(questions),
        "hit_count": hits,
        "recall_at_k": round(hits / len(questions), 6),
        "calculation": "questions with at least one manually linked gold chunk in top-k / total questions",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": [
            "This is a lexical BM25 baseline, not the required dense/hybrid retrieval and reranking system.",
            "The manually linked question set is still marked draft pending independent review.",
            "Arabic-only queries are compared against English-only supplementary sources without translation; cross-language misses are expected to require a multilingual retrieval strategy.",
            "This measures retrieval only, not answer faithfulness or RAGAS metrics.",
        ],
        "results": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"BM25 Recall@{args.top_k}: {hits}/{len(questions)} = "
        f"{hits / len(questions):.1%}; report: {args.report}"
    )


if __name__ == "__main__":
    main()
