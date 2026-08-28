"""
rag/generator.py
────────────────────────────────────────────────────────────────────────────
AQILA — Grounded LLM Generation Module
Owner: M1 — AI / ML + RAG Core

PLACEHOLDER — Implementation begins at Hour 0 of the hackathon.

Responsibilities (per v4.1 §3 M1 + §8 Grounded Generation):
  - Build numbered context prompt from retrieved chunks (TEXT ONLY — no embeddings)
  - Call Ollama llama3.2:3b
    - Temperature: 0.1
    - num_ctx: 4096
    - Grounded prompt: "Answer ONLY using the provided sources. Cite each
      source with [N]. If evidence is insufficient, say so."
  - Extract [N] citation markers from LLM output → Citation objects
  - AQILA uses grounded generation — do NOT claim zero hallucination.
    When evidence is insufficient the system indicates this.

LLM Resource Safety (per v4.1 §8):
  - On ~16 GB RAM / CPU-first hardware, only ONE heavyweight LLM inference
    workload should be active at a time (unless hardware-tested otherwise).
  - llama3.2:3b must be pre-pulled before hackathon. No runtime downloads.
  - Fallback: llama3.2:1b if latency > 35s on demo hardware.

References:
  - docs/API_CONTRACTS.md  — Citation contract
  - backend/.env.example   — OLLAMA_BASE_URL, OLLAMA_MODEL
"""

# TODO (M1, Hour 5–10): Implement generate_answer(), extract_citations()
