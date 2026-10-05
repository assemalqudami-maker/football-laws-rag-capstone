#!/usr/bin/env python3
"""Small, dependency-free BM25 baseline over the generated chunk JSONL."""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHUNKS = ROOT / "data" / "processed" / "chunks.jsonl"
TOKEN_RE = re.compile(r"[\u0621-\u063A\u0641-\u064A\u066E-\u06D3\u06FA-\u06FF]+|[A-Za-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Use conservative Unicode normalization; preserve Arabic diacritics/alef forms."""
    return TOKEN_RE.findall(unicodedata.normalize("NFKC", text).casefold())


def load_chunks(path: Path, include_review_required: bool) -> list[dict]:
    chunks = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            chunk = json.loads(line)
            if chunk.get("review_required") and not include_review_required:
                continue
            chunk["_tokens"] = tokenize(chunk.get("text", ""))
            if chunk["_tokens"]:
                chunks.append(chunk)
    if not chunks:
        raise ValueError(f"No searchable chunks loaded from {path}")
    return chunks


def rank_bm25(chunks: list[dict], query: str, k: int = 5, k1: float = 1.5, b: float = 0.75) -> list[dict]:
    query_terms = tokenize(query)
    if not query_terms:
        return []
    doc_terms = [Counter(chunk["_tokens"]) for chunk in chunks]
    document_frequency = Counter()
    for frequencies in doc_terms:
        document_frequency.update(frequencies.keys())
    average_length = sum(len(chunk["_tokens"]) for chunk in chunks) / len(chunks)
    total_docs = len(chunks)

    ranked = []
    for chunk, frequencies in zip(chunks, doc_terms):
        length = len(chunk["_tokens"])
        score = 0.0
        for term, query_frequency in Counter(query_terms).items():
            term_frequency = frequencies.get(term, 0)
            if not term_frequency:
                continue
            df = document_frequency[term]
            inverse_document_frequency = math.log1p(
                (total_docs - df + 0.5) / (df + 0.5)
            )
            denominator = term_frequency + k1 * (
                1 - b + b * length / average_length
            )
            score += inverse_document_frequency * (
                term_frequency * (k1 + 1) / denominator
            ) * query_frequency
        if score <= 0:
            continue
        refs = chunk.get("source_refs", [])
        ranked.append(
            {
                "chunk_id": chunk["chunk_id"],
                "score": round(score, 6),
                "text": chunk["text"],
                "review_required": chunk.get("review_required", False),
                "source_refs": refs,
            }
        )
    return sorted(ranked, key=lambda item: (-item["score"], item["chunk_id"]))[:k]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Arabic or English question")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--include-review-required", action="store_true")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be positive")
    chunks = load_chunks(args.chunks, args.include_review_required)
    results = rank_bm25(chunks, args.query, args.top_k)
    print(json.dumps({"query": args.query, "retriever": "bm25_baseline", "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
