# Architecture — الحَكَم الذكي

## Architecture status

This is a proposed architecture, not an implemented or measured system yet. Final choices are subject to retrieval tests and the capstone requirements.

## Current corpus and language constraints

The first source is the official Arabic IFAB Laws of the Game 2026/27 PDF (236 pages). The corpus is being expanded with IFAB's 17 current law pages and distinct official guidelines, protocols, and law-change/circular materials. Web pages are separate identifiable IFAB publications and often include practical FAQs; the Arabic PDF provides Arabic law text and printed-page citations. Use source IDs to distinguish documents and deduplicate identical passages during retrieval. Do not cite an English passage as an Arabic quotation; if the retrieved authoritative evidence is English, answer in Arabic and identify the original English source.

## Proposed ingestion flow

```text
Official IFAB laws, guidelines, protocols and circulars
        ↓
PDF/web extraction with original page and source metadata
        ↓
Arabic text normalization (preserve legal wording)
        ↓
Law/section-aware chunking with limited token overlap
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

- Chunking: compare law/section-aware chunks against fixed token windows; do not split numbered clauses if avoidable.
- Embeddings: benchmark multilingual models with Arabic questions against Arabic and English official passages.
- Vector database: compare Chroma with the simplest deployment-compatible alternative after measuring corpus size and host persistence.
- Reranker/LLM: select after checking current pricing, API availability, Arabic quality, and deployment constraints.
- Hosting: choose Hugging Face Spaces or Railway based on actual model footprint, persistent storage, and current free-tier limits.

Document measured comparisons and reasons in `ADR.md` after implementation. Do not claim an architecture is proven until measured.
