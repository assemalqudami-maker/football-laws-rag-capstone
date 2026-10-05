#!/usr/bin/env python3
"""Audit the collected IFAB corpus without external API calls.

Reports source coverage, extracted-text availability, document identity groups,
exact full-document duplicates, and same-language five-token overlap.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "eval" / "corpus_audit.json"
AR_EN_LAW_CHANGES = {
    "IFAB-LAW-CHANGES-2026-27-AR",
    "IFAB-LAW-CHANGES-2026-27-EN",
}


def extracted_path(row: dict[str, str]) -> Path:
    if row["id"] == "IFAB-LOTG-2026-27-AR":
        return ROOT / "data" / "extracted" / "laws_pages.jsonl"
    match = re.search(r"(?:^|;\s*)extracted=([^;]+)", row.get("notes", ""))
    if not match:
        raise ValueError(f"No extracted path recorded for {row['id']}")
    return ROOT / Path(match.group(1).replace("\\", "/"))


def read_source_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() != ".jsonl":
        return raw
    records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return "\n".join(record.get("text", "") for record in records)


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def fivegrams(tokens: list[str]) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + 5]) for i in range(max(0, len(tokens) - 4))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    with (ROOT / "data" / "sources_manifest.csv").open(
        encoding="utf-8-sig", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    docs = []
    missing = []
    for row in rows:
        path = extracted_path(row)
        if not path.is_file():
            missing.append({"source_id": row["id"], "path": str(path)})
            continue
        text = read_source_text(path)
        normalized = normalize(text)
        tokens = re.findall(r"\w+", normalized, flags=re.UNICODE)
        docs.append(
            {
                "source_id": row["id"],
                "title": row["title"],
                "language": row["language"],
                "status": row["status"],
                "extracted_path": path.relative_to(ROOT).as_posix(),
                "character_count": len(text),
                "word_count": len(tokens),
                "sha256_normalized_text": hashlib.sha256(
                    normalized.encode("utf-8")
                ).hexdigest(),
                "fivegrams": fivegrams(tokens),
                "normalized_text": normalized,
            }
        )

    by_hash = defaultdict(list)
    for doc in docs:
        by_hash[doc["sha256_normalized_text"]].append(doc["source_id"])
    exact_duplicates = [ids for ids in by_hash.values() if len(ids) > 1]

    overlaps = []
    for left, right in itertools.combinations(docs, 2):
        if left["language"] != right["language"]:
            continue
        a, b = left["fivegrams"], right["fivegrams"]
        union = len(a | b)
        if not union:
            continue
        similarity = len(a & b) / union
        overlaps.append(
            {
                "source_a": left["source_id"],
                "source_b": right["source_id"],
                "fivegram_jaccard": round(similarity, 4),
                "shared_fivegrams": len(a & b),
            }
        )
    overlaps.sort(key=lambda item: item["fivegram_jaccard"], reverse=True)

    doc_groups = []
    seen = set()
    for doc in docs:
        source_id = doc["source_id"]
        if source_id in AR_EN_LAW_CHANGES:
            group_id = "IFAB-LAW-CHANGES-2026-27"
            title = "Changes to the Laws of the Game 2026/27"
        else:
            group_id = source_id
            title = doc["title"]
        if group_id not in seen:
            doc_groups.append({"document_id": group_id, "title": title})
            seen.add(group_id)

    law_pages = [doc for doc in docs if re.fullmatch(r"IFAB-LAW-\d{2}-2026-27", doc["source_id"])]
    faq_count = sum(
        bool(re.search(r"\bFAQs?\b|Frequently Asked Questions", doc["normalized_text"], re.I))
        for doc in law_pages
    )

    qa_path = ROOT / "data" / "eval" / "extraction_qa.json"
    pdf_qa = json.loads(qa_path.read_text(encoding="utf-8"))
    report = {
        "audit_date": datetime.now(ZoneInfo("Asia/Riyadh")).date().isoformat(),
        "method": {
            "document_identity": (
                "One separately identified official IFAB topical web page or "
                "standalone publication counts once. Internal PDF pages/sections "
                "do not count separately. Arabic and English copies of the same "
                "2026/27 law-changes publication count as one document."
            ),
            "exact_duplicate_check": (
                "NFKC normalization, case-folding, and whitespace collapse, "
                "then SHA-256 of each whole extracted document."
            ),
            "overlap_check": (
                "Five-token shingle Jaccard for same-language document pairs; "
                "this is a review signal, not an automatic deletion rule."
            ),
        },
        "source_entries": len(rows),
        "extracted_source_entries": len(docs),
        "missing_extractions": missing,
        "source_status_counts": dict(Counter(row["status"] for row in rows)),
        "format_counts": dict(Counter(row["format"] for row in rows)),
        "source_document_count_after_translation_merge": len(doc_groups),
        "document_identity_groups": doc_groups,
        "total_extracted_characters": sum(doc["character_count"] for doc in docs),
        "empty_extracted_documents": [
            doc["source_id"] for doc in docs if doc["word_count"] == 0
        ],
        "exact_full_document_duplicate_groups": exact_duplicates,
        "top_same_language_fivegram_overlaps": overlaps[:10],
        "law_webpages_with_faq_marker": {
            "count": faq_count,
            "total": len(law_pages),
        },
        "arabic_lawbook_extraction": {
            "page_count": pdf_qa["page_count"],
            "extractable_pages": pdf_qa["extractable_pages"],
            "total_characters": pdf_qa["total_characters"],
            "median_characters_per_page": pdf_qa["median_characters_per_page"],
            "pages_flagged_for_visual_review": len(
                pdf_qa.get("pages_flagged_for_review", [])
            ),
            "visual_review_complete": False,
        },
        "source_documents": [
            {key: value for key, value in doc.items() if key not in {"fivegrams", "normalized_text"}}
            for doc in docs
        ],
        "limitations": [
            "Text extractability does not prove that every extracted clause is accurate.",
            "The Arabic lawbook pages flagged by extraction QA still need visual checking.",
            "High fivegram overlap is reported for review; clauses are not deleted automatically.",
            "The Arabic/English law-changes pair is one document identity with two language representations.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {args.output.relative_to(ROOT)}: "
        f"{report['source_document_count_after_translation_merge']} document identities, "
        f"{len(docs)} extracted source entries, {len(missing)} missing extractions, "
        f"{len(exact_duplicates)} exact-duplicate groups, "
        f"{faq_count}/{len(law_pages)} law pages contain FAQ markers."
    )


if __name__ == "__main__":
    main()
