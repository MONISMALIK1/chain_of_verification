# chain_of_verification

[![tests](https://github.com/MONISMALIK1/chain_of_verification/actions/workflows/test.yml/badge.svg)](https://github.com/MONISMALIK1/chain_of_verification/actions/workflows/test.yml)

A from-scratch, dependency-free implementation of **Chain-of-Verification (CoVe)** —
a prompting method that **reduces hallucination by making the model fact-check
itself**. It drafts an answer, plans questions to verify its own claims, answers
those questions *independently*, and revises the draft to keep only what holds up.

> Dhuliawala, Komeili, Xu, Raileanu, Li, Celikyilmaz, Weston (2023),
> *Chain-of-Verification Reduces Hallucination in Large Language Models.*
> [arXiv:2309.11495](https://arxiv.org/abs/2309.11495)

## The four steps

```
question: "Name some politicians born in New York City."
   │
(i) DRAFT ───────▶ "Donald Trump, Hillary Clinton, Franklin D. Roosevelt"   (2 are wrong)
   │
(ii) PLAN ───────▶ "Where was Donald Trump born?"
                   "Where was Hillary Clinton born?"
                   "Where was Franklin D. Roosevelt born?"
   │
(iii) VERIFY ────▶ each answered IN ISOLATION (the draft is not shown):
                   Trump → New York City     ✓
                   Clinton → Chicago         ✗
                   Roosevelt → Hyde Park, NY ✗
   │
(iv) REVISE ─────▶ "Donald Trump." — keeps only what the verifications support
```

**Why answer the verification questions independently?** That's the crux of the
paper's *factored* variant. If the model re-reads its own draft while verifying, it
tends to repeat the original mistake. Answered in isolation, each fact is checked on
its own merits — so a hallucination can't confirm itself. This implementation always
factors the verification step (see `core.answer_verification`).

## How it fits the series

It's the **reflection-without-retrieval** counterpart to the RAG repos:
[self_rag](https://github.com/MONISMALIK1/self_rag) and
[corrective_rag](https://github.com/MONISMALIK1/corrective_rag) critique *retrieved
passages*; CoVe critiques the model's *own answer* using nothing but more questions.

## Install

No third-party dependencies. Python 3.11+.

```bash
git clone https://github.com/MONISMALIK1/chain_of_verification.git
cd chain_of_verification && pip install -e .      # optional; or run from the parent dir
```

Point it at any OpenAI-compatible backend:

```bash
export OPENROUTER_API_KEY=sk-or-...                                   # OpenRouter (default)
# …or a local model:
export COVE_BASE_URL=http://localhost:11434/v1/chat/completions       # Ollama
export COVE_MODEL=qwen2.5:7b
```

## Use

```bash
# answer with self-verification
python -m chain_of_verification "Name some politicians born in New York City."

# show the draft, the independent verification Q&A, and the final answer
python -m chain_of_verification "Who composed The Four Seasons?" --show-steps

# cap how many verification questions get asked
python -m chain_of_verification "..." --max-questions 3
```

CoVe helps most on questions a model answers *fluently but wrongly* — list-style
("name all…"), entity attributes (dates, places, authorship), and other facts that
are easy to state and easy to get subtly wrong.

## Design

The control flow is plain stdlib and unit-tested offline; only the four model calls
touch the network (via the injectable `chat_fn`).

| Module | Responsibility |
| --- | --- |
| `prompts.py` | the four prompts: draft, plan, verify (isolated), revise |
| `core.py` | the pipeline → `CoVeResult`, plus pure verification-question parsing |
| `llm.py` | backend-agnostic OpenAI-compatible client (OpenRouter or local) |

## Test

```bash
make test        # or: python -m unittest discover -s chain_of_verification/tests -t . -v
```

11 offline tests, no API key required — driving the full draft→plan→verify→revise
flow with a scripted model, and asserting the key property: each verification is
answered **in isolation** (its prompt never contains the draft or the other
questions), plus list parsing and the no-questions short-circuit.

## Limitations

- **It's still the same model checking itself.** CoVe helps when the model *knows*
  the fact but mis-stated it in the draft; it can't verify something the model simply
  doesn't know (the verification answer may be wrong too).
- **Cost.** One draft + one plan + one call per verification question + one revision.
  `--max-questions` caps the middle.
- **No external ground truth.** This implements the factored variant; wiring the
  verification answers to a retriever or tool (so they're checked against *evidence*,
  not just the model) is a natural extension.

## License

MIT
