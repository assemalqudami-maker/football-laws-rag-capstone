"""Extract searchable PDF text page by page while preserving page metadata.

This first-pass extractor deliberately does not attempt OCR or reorder complex
RTL/multi-column pages. Review the generated QA report before ingestion.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path

import fitz


def normalize(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--qa", type=Path, required=True)
    args = parser.parse_args()

    doc = fitz.open(args.pdf)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.qa.parent.mkdir(parents=True, exist_ok=True)
    issues: list[dict[str, object]] = []
    page_lengths: list[int] = []
    quality_counts: Counter[str] = Counter()

    with args.out.open("w", encoding="utf-8") as target:
        for index, page in enumerate(doc):
            # Keep the PDF content order; geometric sorting can scramble RTL text.
            text = normalize(page.get_text("text", sort=False))
            page_lengths.append(len(text))
            arabic_chars = len(re.findall(r"[\u0600-\u06ff]", text))
            replacement_count = text.count("\ufffd")
            # Some low control codes are used by this PDF's font map as layout
            # markers (for example bullets). Keep them unchanged. Flag only
            # unexpected C1 controls and replacement glyphs for source comparison.
            formatting_marker_count = sum(
                1 for char in text if ord(char) in {2, 5, 7, 22, 30}
            )
            unexpected_control_count = sum(
                1 for char in text
                if (ord(char) < 32 and char not in "\n\t\r" and ord(char) not in {2, 5, 7, 22, 30})
                or 127 <= ord(char) <= 159
            )
            if len(text) < 25:
                quality = "visual_or_cover"
            elif len(text) < 100:
                quality = "short_visual_or_text"
            elif replacement_count or unexpected_control_count:
                quality = "text_needs_visual_check"
            else:
                quality = "text_extractable_review_sample"
            quality_counts[quality] += 1
            record = {
                "source_id": "IFAB-LOTG-2026-27-AR",
                "source_title": "Laws of the Game 2026/27 (Arabic)",
                "season": "2026/27",
                "pdf_page": index + 1,
                "text": text,
                "quality_status": quality,
                "char_count": len(text),
                "arabic_char_count": arabic_chars,
                "replacement_character_count": replacement_count,
                "formatting_marker_count": formatting_marker_count,
                "unexpected_control_character_count": unexpected_control_count,
            }
            target.write(json.dumps(record, ensure_ascii=False) + "\n")

            # Flag pages without enough text. Graphic detection is handled separately:
            # vector diagrams are common even on text-rich pages.
            if len(text) < 100:
                issues.append({"pdf_page": index + 1, "reason": quality, "chars": len(text)})
            if replacement_count or unexpected_control_count:
                issues.append({
                    "pdf_page": index + 1,
                    "reason": "suspicious_extracted_glyph_or_control",
                    "chars": len(text),
                    "replacement_character_count": replacement_count,
                    "formatting_marker_count": formatting_marker_count,
                    "unexpected_control_character_count": unexpected_control_count,
                })

    args.qa.write_text(
        json.dumps(
            {
                "source": str(args.pdf),
                "page_count": len(doc),
                "extractable_pages": len(doc),
                "total_characters": sum(page_lengths),
                "median_characters_per_page": statistics.median(page_lengths) if page_lengths else 0,
                "quality_counts": dict(quality_counts),
                "pages_flagged_for_review": issues,
                "warning": "Extracted text is preserved verbatim. Pages classified as visual_or_cover or short_visual_or_text are not assumed blank; inspect them for diagrams/tables. Pages with suspicious glyphs need comparison with the rendered PDF. No OCR is performed.",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Extracted {len(doc)} pages to {args.out}")
    print(f"Flagged {len(issues)} pages for visual review; see {args.qa}")


if __name__ == "__main__":
    main()
