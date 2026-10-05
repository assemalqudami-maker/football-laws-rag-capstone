# Arabic PDF extraction review

## Sample inspected

Rendered the official Arabic IFAB 2026/27 lawbook and compared PDF pages 6, 91, 224, and 228 with both the primary PyMuPDF extraction and the separate PyPDF candidate.

| PDF page | Visual content | Review finding |
|---:|---|---|
| 6 | Table of contents | Page is readable in the PDF. The primary extraction has a few replacement glyphs in headings; this page is navigational front matter and should not be used as legal evidence. |
| 91 | Law 7 — Duration of the Match | The primary extraction preserves the substantive Arabic clauses and their order more clearly. PyPDF removes replacement glyphs but drops or truncates text and headings. |
| 224 | Offside diagrams and captions | The primary extraction retains the captions and legend, with replacement glyphs in several words. The diagram itself is not represented as searchable prose. |
| 228 | Offside diagrams and captions | The primary extraction retains the explanatory captions better than the PyPDF candidate, but the diagrams carry visual context not available from plain text alone. |

## Decision

Keep PyMuPDF as the current primary extractor. The PyPDF candidate is not a correction: its zero replacement-glyph count does not mean its text is more accurate. Do not replace glyphs globally or choose an extractor using replacement-character count alone.

For ingestion, exclude navigational front matter from legal evidence. Keep diagram captions only as text evidence, with page citation, and do not claim the text describes every visual detail. Preserve flagged pages for manual review or exclude a flagged passage when its wording is uncertain.

## Review status

This is a four-page sample, not a complete manual review. The extraction QA still flags 57 pages for suspicious glyphs/controls, 44 visual-or-cover pages, and 12 short pages. The complete visual review remains open. No OCR has been run.
