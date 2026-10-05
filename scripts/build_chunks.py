#!/usr/bin/env python3
"""Build citation-preserving, structure-aware text chunks from extracted IFAB data.

This script uses only the Python standard library and makes no model/API calls.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "chunks.jsonl"
DEFAULT_REPORT = ROOT / "data" / "eval" / "chunk_build_report.json"
REVIEW_STATUSES = {
    "text_needs_visual_check",
    "visual_or_cover",
    "short_visual_or_text",
}


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip()


def split_long_block(block: str, max_words: int) -> list[str]:
    if len(block.split()) <= max_words:
        return [block]

    sentences = re.split(r"(?<=[.!?؟؛])\s+", block)
    output: list[str] = []
    current: list[str] = []
    current_words = 0
    for sentence in sentences:
        words = sentence.split()
        if len(words) > max_words:
            if current:
                output.append(" ".join(current))
                current, current_words = [], 0
            for start in range(0, len(words), max_words):
                output.append(" ".join(words[start : start + max_words]))
            continue
        if current and current_words + len(words) > max_words:
            output.append(" ".join(current))
            current, current_words = [], 0
        current.append(sentence)
        current_words += len(words)
    if current:
        output.append(" ".join(current))
    return output


def make_chunks(text: str, max_words: int, overlap_words: int) -> list[str]:
    # Reserve enough space for carry-over so the inclusive chunk ceiling remains
    # bounded even when the next legal paragraph is itself long.
    block_limit = max(1, max_words - overlap_words)
    blocks = [
        part.strip()
        for line in text.splitlines()
        if line.strip()
        for part in split_long_block(line.strip(), block_limit)
    ]
    if not blocks:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_words = 0
    for block in blocks:
        block_words = len(block.split())
        if current and current_words + block_words > max_words:
            previous = "\n".join(current)
            chunks.append(previous)
            tail = previous.split()[-overlap_words:] if overlap_words else []
            current = [" ".join(tail), block] if tail else [block]
            current_words = len(tail) + block_words
        else:
            current.append(block)
            current_words += block_words
    if current:
        chunks.append("\n".join(current))
    return [chunk for chunk in chunks if chunk.strip()]


def read_jsonl_pages(path: Path) -> list[dict]:
    pages = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                pages.append(json.loads(line))
    return pages


def iter_documents(manifest: list[dict[str, str]]):
    for row in manifest:
        source_id = row["id"]
        if source_id == "IFAB-LOTG-2026-27-AR":
            extracted = ROOT / "data" / "extracted" / "laws_pages.jsonl"
        else:
            match = re.search(r"(?:^|;\s*)extracted=([^;]+)", row.get("notes", ""))
            if not match:
                raise ValueError(f"No extracted file path in manifest for {source_id}")
            extracted = ROOT / Path(match.group(1).replace("\\", "/"))
        if not extracted.is_file():
            raise FileNotFoundError(f"Missing extracted file for {source_id}: {extracted}")

        if extracted.suffix.lower() == ".jsonl":
            pages = read_jsonl_pages(extracted)
        else:
            pages = [{"text": extracted.read_text(encoding="utf-8"), "pdf_page": None}]
        yield row, extracted, pages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-words", type=int, default=360)
    parser.add_argument("--overlap-words", type=int, default=55)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    if args.max_words < 80 or args.overlap_words < 0 or args.overlap_words >= args.max_words:
        parser.error("Use max-words >= 80 and 0 <= overlap-words < max-words.")

    with (ROOT / "data" / "sources_manifest.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        manifest = list(csv.DictReader(handle))

    extraction_qa = json.loads(
        (ROOT / "data" / "eval" / "extraction_qa.json").read_text(encoding="utf-8")
    )
    qa_flagged_pages = {
        page["pdf_page"] for page in extraction_qa.get("pages_flagged_for_review", [])
    }
    unique: dict[str, dict] = {}
    input_page_count = 0
    missing_text_pages = []
    excluded_front_matter_pages = []
    flagged_pages_seen_after_front_matter_filter = set()
    source_chunk_counts: Counter[str] = Counter()
    review_chunk_count = 0
    pre_dedupe_count = 0

    for row, extracted, pages in iter_documents(manifest):
        for page in pages:
            input_page_count += 1
            text = page.get("text", "")
            page_no = page.get("pdf_page")
            if row["id"] == "IFAB-LOTG-2026-27-AR" and page_no is not None and page_no <= 8:
                excluded_front_matter_pages.append(page_no)
                continue
            quality_status = page.get("quality_status")
            needs_review = quality_status in REVIEW_STATUSES or (
                row["id"] == "IFAB-LOTG-2026-27-AR" and page_no in qa_flagged_pages
            )
            if needs_review:
                flagged_pages_seen_after_front_matter_filter.add(page_no)
            if not normalize_text(text):
                missing_text_pages.append(
                    {"source_id": row["id"], "pdf_page": page_no}
                )
                continue
            page_chunks = make_chunks(text, args.max_words, args.overlap_words)
            for chunk_index, chunk_text in enumerate(page_chunks, start=1):
                normalized = normalize_text(chunk_text)
                if len(normalized.split()) < 8:
                    continue
                pre_dedupe_count += 1
                digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
                source_ref = {
                    "source_id": row["id"],
                    "source_title": row["title"],
                    "url": row["url"],
                    "language": row["language"],
                    "season": row["season"],
                    "pdf_page": page_no,
                    "format": row["format"],
                    "quality_status": quality_status,
                }
                if digest in unique:
                    item = unique[digest]
                    if source_ref not in item["source_refs"]:
                        item["source_refs"].append(source_ref)
                    item["review_required"] = item["review_required"] or needs_review
                    item["duplicate_occurrences"] += 1
                    continue
                chunk_id = hashlib.sha256(
                    f"{row['id']}:{page_no}:{chunk_index}:{digest}".encode("utf-8")
                ).hexdigest()[:20]
                unique[digest] = {
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "word_count": len(chunk_text.split()),
                    "character_count": len(chunk_text),
                    "source_refs": [source_ref],
                    "review_required": needs_review,
                    "duplicate_occurrences": 1,
                }
                source_chunk_counts[row["id"]] += 1
                if needs_review:
                    review_chunk_count += 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Dict insertion order follows manifest, source, and page order.
    ordered = list(unique.values())
    with args.out.open("w", encoding="utf-8") as handle:
        for item in ordered:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    word_counts = [item["word_count"] for item in ordered]
    report = {
        "chunking_strategy": {
            "name": "page-preserving, paragraph-aware word-window baseline",
            "max_words": args.max_words,
            "overlap_words": args.overlap_words,
            "rationale": (
                "Keep PDF page boundaries and source metadata for exact citations; "
                "accumulate extracted paragraphs/lines up to a bounded word window; "
                "use modest overlap only when a page or source document continues across "
                "the chunk boundary. This is a baseline to compare using retrieval "
                "questions before finalizing."
            ),
        },
        "source_count": len(manifest),
        "input_page_or_document_units": input_page_count,
        "pages_marked_for_review": len(qa_flagged_pages),
        "flagged_pages_remaining_after_front_matter_exclusion": len(flagged_pages_seen_after_front_matter_filter),
        "excluded_front_matter_pages": sorted(excluded_front_matter_pages),
        "empty_text_units": missing_text_pages,
        "chunks_before_exact_deduplication": pre_dedupe_count,
        "chunks_after_exact_deduplication": len(ordered),
        "duplicate_occurrences_merged": pre_dedupe_count - len(ordered),
        "chunks_marked_review_required": sum(item["review_required"] for item in ordered),
        "chunk_word_count": {
            "min": min(word_counts, default=0),
            "median": statistics.median(word_counts) if word_counts else 0,
            "max": max(word_counts, default=0),
            "mean": round(statistics.mean(word_counts), 2) if word_counts else 0,
        },
        "per_source_chunk_counts": dict(source_chunk_counts),
        "output": args.out.relative_to(ROOT).as_posix()
        if args.out.is_relative_to(ROOT)
        else str(args.out),
        "warnings": [
            "Word counts approximate tokenizer tokens; compare chunk sizes with the selected embedding model.",
            "Pages flagged by extraction QA remain marked review_required; chunking does not certify text accuracy.",
            "Exact deduplication merges identical text while retaining all source references.",
        ],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Built {len(ordered)} chunks from {len(manifest)} sources "
        f"({pre_dedupe_count - len(ordered)} exact duplicates merged); "
        f"{report['chunks_marked_review_required']} chunks need source review."
    )
    print(f"Wrote {args.out} and {args.report}")


if __name__ == "__main__":
    main()
