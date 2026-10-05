# Candidate official IFAB corpus for Football Laws RAG

The collected manifest contains 33 official IFAB source records: 17 law-specific web pages, 12 supplementary HTML pages, three supplementary PDF records, and the Arabic lawbook. All 33 have extracted text. The Arabic and English 2026/27 law-changes PDFs are language versions of one publication, so the corpus audit counts 32 document identities. Each of the 17 law-specific web pages has a distinct official URL and a FAQ marker in its extracted text; the project counts these as separate topical reference documents, not as pages of the Arabic lawbook. The instructor-facing count methodology and extraction/overlap checks are in `corpus_audit.md` and `corpus_audit.json`.

## Sources currently recorded

| ID | Source | Language | Format | Status | URL |
|---|---|---|---|---|---|
| IFAB-LAW-01-2026-27 | Law 1 — The Field of Play | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-field-of-play/ |
| IFAB-LAW-02-2026-27 | Law 2 — The Ball | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-ball/ |
| IFAB-LAW-03-2026-27 | Law 3 — The Players | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-players/ |
| IFAB-LAW-04-2026-27 | Law 4 — The Players’ Equipment | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-players-equipment/ |
| IFAB-LAW-05-2026-27 | Law 5 — The Referee | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-referee/ |
| IFAB-LAW-06-2026-27 | Law 6 — The Other Match Officials | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-other-match-officials/ |
| IFAB-LAW-07-2026-27 | Law 7 — The Duration of the Match | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-duration-of-the-match/ |
| IFAB-LAW-08-2026-27 | Law 8 — Start and Restart of Play | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-start-and-restart-of-play/ |
| IFAB-LAW-09-2026-27 | Law 9 — The Ball in and out of Play | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-ball-in-and-out-of-play/ |
| IFAB-LAW-10-2026-27 | Law 10 — Determining the Outcome of a Match | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/determining-the-outcome-of-a-match/ |
| IFAB-LAW-11-2026-27 | Law 11 — Offside | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/offside/ |
| IFAB-LAW-12-2026-27 | Law 12 — Fouls and Misconduct | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/fouls-and-misconduct/ |
| IFAB-LAW-13-2026-27 | Law 13 — Free Kicks | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/free-kicks/ |
| IFAB-LAW-14-2026-27 | Law 14 — The Penalty Kick | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-penalty-kick/ |
| IFAB-LAW-15-2026-27 | Law 15 — The Throw-in | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-throw-in/ |
| IFAB-LAW-16-2026-27 | Law 16 — The Goal Kick | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-goal-kick/ |
| IFAB-LAW-17-2026-27 | Law 17 — The Corner Kick | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/the-corner-kick/ |
| IFAB-VAR-2026-27 | Video Assistant Referee (VAR) protocol | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/video-assistant-referee-var-protocol/ |
| IFAB-TIME-SUB-2026-27 | Time-limited substitution protocol | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/time-limited-substitution-protocol/ |
| IFAB-OFFFIELD-TREATMENT-2026-27 | Off-field treatment and assessment protocol | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/off-field-treatment-and-assessment-protocol/ |
| IFAB-THROW-GOALKICK-2026-27 | Throw-in and goal-kick countdown protocol | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/throw-in-and-goal-kick-countdown-protocol/ |
| IFAB-CAPTAIN-GUIDELINES | Only the captain guidelines | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/only-the-captain/ |
| IFAB-TEMP-DISMISSALS | Guidelines for Temporary Dismissals | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines-for-temporary-dismissals/ |
| IFAB-RETURN-SUBS | Guidelines for Return Substitutes | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines-for-return-substitutes/ |
| IFAB-CONCUSSION-SUBS | Additional permanent concussion substitutions protocol | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/additional-permanent-concussion-substitutions-protocol/ |
| IFAB-GUIDE-INTRO | Guidelines for Match Officials — Introduction | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines/introduction/ |
| IFAB-GUIDE-POSITIONING | Guidelines — Positioning, movement and teamwork | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines/positioning-movement-and-teamwork/ |
| IFAB-GUIDE-COMMS | Guidelines — Body language, communication and whistle | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines/body-language-communication-and-whistle/ |
| IFAB-GUIDE-ADVICE | Guidelines — Other advice | English | HTML | downloaded_and_extracted | https://www.theifab.com/laws/latest/guidelines/other-advice/ |
| IFAB-LAW-CHANGES-2026-27-AR | Changes to the Laws of the Game 2026/27 (Arabic) | Arabic | PDF | downloaded_and_extracted | https://www.theifab.com/downloads/changes-to-the-laws-of-the-game-202627-arabic?l=en |
| IFAB-LAW-CHANGES-2026-27-EN | Changes to the Laws of the Game 2026/27 | English | PDF | downloaded_and_extracted | https://www.theifab.com/downloads/changes-to-the-laws-of-the-game-202627?l=en |
| IFAB-CIRCULAR-32-2026 | Circular 32 (2026) | English | PDF | downloaded_and_extracted | https://www.theifab.com/downloads/circular-32?l=en |
| IFAB-LOTG-2026-27-AR | Laws of the Game 2026/27 (Arabic) | Arabic | PDF | downloaded_and_text_extractable | https://www.theifab.com/laws-of-the-game-documents/?language=all&year=2026%2F27 |

## Collection and inclusion rules

- Download only from official IFAB domains and verify file type, page title, edition, and text extraction.
- Capture retrieval date and SHA-256 for each downloaded item.
- Keep the Arabic PDF as the Arabic law text and page citation reference. Index official English law pages as separately identified sources only after deduplication and mixed-language retrieval checks.
- Exclude old seasons, other football codes, and trials that are not applicable to the 2026/27 laws unless their status is clearly labelled.
- Full-document audit found no exact normalized duplicate texts. The highest same-language five-token Jaccard overlap is 0.1313 between the Arabic law-changes publication and Arabic lawbook; this is expected overlap and does not justify dropping either source. Deduplicate exact chunks at indexing time while preserving original citations.
- The instructor asks for 20–50 documents. Current count is 32 document identities from 33 extracted source records after merging the Arabic/English law-changes translation pair. See the audit methodology and the note about confirming the instructor's interpretation of topical web pages.
- Do not count PDF pages, chunks, repeated editions, or translations as separate documents. Count a separately published topical web reference only when it has its own official URL and substantive content; the 17 law pages meet this criterion and all have FAQ markers.
- Official law text is available in English, French, German and Spanish; IFAB notes that the English version is authoritative if wording diverges. Arabic remains the user-facing language; expose source language and cite exact document/section/page.
- Keep failed downloads in the report as failures; do not fabricate corpus entries or scores. Current report has 33/33 extracted entries and zero failures; visual review of 113 flagged lawbook pages remains incomplete.
