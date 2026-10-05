# API key plan — الحَكَم الذكي

## What the assignment means by an API key

The API key is a secret credential used by an external service, such as a hosted language model, embedding model, or reranker. It is not a submission item by itself. The assignment's limited balance is a usage cap, so provider and model selection must be based on the cap allocated to the student and the actual Arabic retrieval tests. No provider has been selected yet.

## Safe handling

- Never paste a real key into chat, source code, a public GitHub repository, screenshots, or evaluation reports.
- Keep a real key only in a local `.env` file (ignored by Git) during development, and configure deployment secrets through the host's secret settings.
- Commit only an `.env.example` containing empty placeholders after the provider is chosen.
- If a key is accidentally exposed, revoke it in the provider dashboard and create a replacement.

## Keep usage within the cap

1. Ask the supervisor which provider/key was allocated and its remaining cap. Share only the provider name and cap here, never the secret key.
2. First test one short document and one query. Record token usage and cost.
3. Download and clean the corpus before indexing; create the index once and persist it. Do not embed the entire corpus inside a per-question or per-user loop.
4. Run retrieval checks locally without generation where possible. Run RAGAS on the required 20 questions only after retrieval and answers are stable; avoid repeated full runs.
5. Add caching, request limits, short prompts, and a usage log. Include embedding, generation, reranking, and hosting costs in the final scenarios.

## Decision status

Provider, model, and budget remain unconfirmed. This is intentional: choose them only after the allocated API details are known, then document the measured Arabic quality and cost in `architecture.md` and the one-page ADR.
