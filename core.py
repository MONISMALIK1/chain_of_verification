"""The Chain-of-Verification control flow.

Reference: Dhuliawala et al. 2023, "Chain-of-Verification Reduces Hallucination in
Large Language Models", https://arxiv.org/abs/2309.11495

    question
       |
    (i)   draft a baseline answer
       |
    (ii)  plan verification questions that fact-check the draft's claims
       |
    (iii) answer each verification question INDEPENDENTLY (the factored variant) --
          in isolation, so a hallucinated claim can't prime its own confirmation
       |
    (iv)  revise: keep only what the verifications support, drop/correct the rest

Only the model calls touch the network (injectable ``chat_fn``); question parsing
is pure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .llm import chat
from .prompts import BASELINE_PROMPT, PLAN_PROMPT, REVISE_PROMPT, VERIFY_PROMPT

# Strip an optional leading "1.", "2)", "-", "*", "•" from a list item.
_BULLET = re.compile(r"^\s*(?:\d+[.)]\s*|[-*•]\s*)?(.*\S)\s*$")
_SKIP_PREFIXES = ("verification question", "here are", "questions:", "draft answer")


@dataclass
class Verification:
    question: str
    answer: str


@dataclass
class CoVeResult:
    question: str
    baseline: str                       # the unverified draft
    final: str                          # the verified answer
    verifications: list[Verification] = field(default_factory=list)


def parse_questions(text: str) -> list[str]:
    """Pull verification questions out of a model's plan (one per line)."""
    out: list[str] = []
    for line in text.splitlines():
        m = _BULLET.match(line)
        if not m:
            continue
        q = m.group(1).strip()
        if not q or q.lower().startswith(_SKIP_PREFIXES):
            continue
        out.append(q)
    return out


def baseline_answer(question: str, chat_fn=chat, model: str | None = None) -> str:
    return chat_fn(BASELINE_PROMPT.format(question=question), model=model).strip()


def plan_verifications(question: str, baseline: str, chat_fn=chat, model: str | None = None,
                       max_questions: int = 5) -> list[str]:
    raw = chat_fn(PLAN_PROMPT.format(question=question, baseline=baseline), model=model)
    return parse_questions(raw)[:max_questions]


def answer_verification(vq: str, chat_fn=chat, model: str | None = None) -> str:
    """Answer one verification question in isolation — the prompt contains only it."""
    return chat_fn(VERIFY_PROMPT.format(question=vq), model=model).strip()


def revise(question: str, baseline: str, verifications: list[Verification],
           chat_fn=chat, model: str | None = None) -> str:
    block = "\n".join(f"Q: {v.question}\nA: {v.answer}" for v in verifications)
    return chat_fn(REVISE_PROMPT.format(question=question, baseline=baseline,
                                        verifications=block), model=model).strip()


def verify(question: str, max_questions: int = 5, chat_fn=chat,
           model: str | None = None) -> CoVeResult:
    """Run the full CoVe pipeline for ``question``."""
    base = baseline_answer(question, chat_fn=chat_fn, model=model)

    questions = plan_verifications(question, base, chat_fn=chat_fn, model=model,
                                   max_questions=max_questions)
    if not questions:
        # Nothing to check — the draft stands as the final answer.
        return CoVeResult(question=question, baseline=base, final=base, verifications=[])

    verifications = [
        Verification(q, answer_verification(q, chat_fn=chat_fn, model=model))
        for q in questions
    ]
    final = revise(question, base, verifications, chat_fn=chat_fn, model=model)
    return CoVeResult(question=question, baseline=base, final=final,
                      verifications=verifications)


__all__ = [
    "Verification", "CoVeResult", "parse_questions", "baseline_answer",
    "plan_verifications", "answer_verification", "revise", "verify",
]
