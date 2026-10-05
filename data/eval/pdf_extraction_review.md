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

## Additional targeted review

Pages 59, 60, 91, and 101 were rendered and visually checked against the primary extraction for the specific questions that cite them. The rule text needed for the minimum-player rule, half-time interval, and goal conditions is readable. On page 101, the keeper-throw clause says a goal kick is awarded. Page 59 also specifies the narrow case where the referee may allow play to continue if players deliberately leave and the count falls below seven; play cannot be restarted after the ball goes out until the minimum is met. It does not support adding unrelated temporary-protocol exceptions to that answer.

The structured record in `pdf_manual_review.json` records both the scope and limitations of these checks. The original extraction QA still reports 113 flagged pages (57 suspicious glyph/control pages, 44 visual-or-cover pages, and 12 short pages). Pages 59, 60, 91, and 101 have had targeted content review, while the remaining flagged pages still need review; pages 224 and 228 remain flagged because the diagrams and glyph issues need separate treatment. No OCR has been run.
