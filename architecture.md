# Architecture — الحَكَم الذكي

## Architecture status

The corpus audit and baseline chunk builder are implemented. Embeddings, vector storage, reranking, and answer generation remain proposed and unmeasured; final choices depend on Arabic retrieval tests and the assigned API budget.

## Current corpus and language constraints

The collected manifest has 33 extracted records (29 HTML, 4 PDF), representing 32 document identities after merging the Arabic and English 2026/27 law-changes files as one publication. This includes the Arabic IFAB Laws of the Game book, 17 separately published law-topic pages, and supplementary guidelines, protocols, and circular material. All 17 law-topic pages have FAQ markers in their extracted text. The document-count rule and evidence are recorded in `data/eval/corpus_audit.md`. The Arabic book has 236/236 text-extractable pages, but 113 pages are flagged for visual review. Use source IDs to distinguish references and remove exact duplicate chunks only after preserving citations. Do not cite English text as an Arabic quotation; answer in Arabic and identify the source language.

## Proposed ingestion flow

```text
Official IFAB laws, guidelines, protocols and circulars
        ↓
PDF/web extraction with original page and source metadata
        ↓
Arabic text normalization (preserve legal wording)
        ↓
Page/paragraph-aware word-window chunking; preserve citations
        ↓
Multilingual embedding model + lexical BM25 index
        ↓
Persistent vector store
```

Do not strip Arabic diacritics or normalize alef/hamza variants until an ablation shows retrieval improves without harming citations. Preserve the original excerpt for display even if a normalized copy is used for search.

## Proposed query flow

```text
Arabic question
        ↓
Query normalization / multilingual query embedding
        ↓
Vector Top-K + BM25 Top-K
        ↓
Reciprocal Rank Fusion
        ↓
Cross-encoder or hosted reranker (selected after resource/cost tests)
        ↓
Top 5 evidence chunks
        ↓
LLM answer constrained to evidence + page/law citations
```

The generator must abstain when evidence is insufficient. Show the source title, season, law number, PDF page, and an evidence excerpt.

## Decisions still open

- Chunking baseline implemented: `scripts/build_chunks.py` preserves PDF page boundaries, groups extracted lines/paragraphs up to 360 whitespace-delimited words, and overlaps 55 words across chunk boundaries within the same page or source document. It produces 597 chunks (median 325 words) and flags 61 chunks whose pages need review. Compare this baseline with section-boundary and fixed-token variants using the gold questions before finalizing; whitespace words are only an approximation of the selected model tokenizer.
- Embeddings: benchmark multilingual models with Arabic questions against Arabic and English official passages.
- Vector database: compare Chroma with the simplest deployment-compatible alternative after measuring corpus size and host persistence.
- Reranker/LLM: select after checking current pricing, API availability, Arabic quality, and deployment constraints.
- Hosting: choose Hugging Face Spaces or Railway based on actual model footprint, persistent storage, and current free-tier limits.

Document measured comparisons and reasons in `ADR.md` after implementation. Do not claim an architecture is proven until measured.
