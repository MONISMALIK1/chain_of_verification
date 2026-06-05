"""Chain-of-Verification (CoVe) — from scratch, dependency-free.

Reduce hallucination by making the model fact-check itself: draft an answer, plan
verification questions, answer them *independently*, then revise to keep only what
the verifications support.

Reference: Dhuliawala et al., 2023, "Chain-of-Verification Reduces Hallucination in
Large Language Models", https://arxiv.org/abs/2309.11495
"""

from __future__ import annotations

__version__ = "0.1.0"

from .core import (CoVeResult, Verification, answer_verification, baseline_answer,
                   parse_questions, plan_verifications, revise, verify)

__all__ = [
    "__version__",
    "CoVeResult", "Verification", "verify",
    "baseline_answer", "plan_verifications", "answer_verification", "revise",
    "parse_questions",
]
