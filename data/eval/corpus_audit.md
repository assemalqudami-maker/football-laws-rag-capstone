# Corpus audit — الحَكَم الذكي

## Audit result

- **33 source records** are present in the manifest and have extracted text: 29 HTML and 4 PDF records.
- **32 document identities** are counted after treating the Arabic and English copies of “Changes to the Laws of the Game 2026/27” as one publication.
- The 17 law-specific IFAB web references are counted as separate topical documents because each has its own official URL and separately extracted content; **all 17 contain a FAQ marker**. They are not counted by splitting pages or clauses from the Arabic lawbook.
- All 33 source records map to a non-empty extracted text file. The collection report records zero failed downloads.
- A whole-document comparison using NFKC normalization, case-folding, and collapsed whitespace found **no exact duplicate documents**.

## Overlap checks

Five-token shingle Jaccard is calculated between documents in the same language. It is a review signal; it does not automatically remove text. The highest measured overlap is **0.1313** between the Arabic 2026/27 law-changes document and the Arabic lawbook, which is expected because the changes are reflected in the book. Other overlap candidates are ordinary shared legal wording between related laws.

At ingestion time, retain the original source ID, language, season, and page/section citation. Remove an exact duplicate chunk only when the normalized text is identical and preserve its source references. Do not use the overlap score alone to drop evidence.

## Arabic PDF extraction limits

The 236-page Arabic lawbook has extractable text on all 236 pages (215,895 characters; median 1,033 characters per page). The extraction QA marks **113 pages for visual review** because they are covers, diagrams, short pages, or otherwise need inspection. A four-page visual comparison is documented in `pdf_extraction_review.md`: it supports keeping PyMuPDF as the primary extractor, but it is only a sample. Visual review is not yet complete, so the text is not certified as fully accurate.

## Count interpretation for the assignment

The project uses “document” to mean a separately identified official publication or substantive official topical reference page with its own source ID and URL. The 17 law-topic pages qualify as independent IFAB references because they include their own law-specific text and FAQ material; they are not fabricated subdivisions of the PDF. The two language versions of one law-changes publication count once. This yields 32 documents, within the required 20–50 range.

If the supervisor interprets “document” more narrowly and excludes topical web references, confirm that interpretation before submission rather than relabeling pages or inflating the count.

## Reproduce the audit

From the project root, run:

```bash
python scripts/audit_corpus.py
```

The command writes `data/eval/corpus_audit.json`. It makes no network or API calls.
