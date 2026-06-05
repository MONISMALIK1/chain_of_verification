"""CLI for Chain-of-Verification.

Usage:
    # Answer a question with self-verification
    python -m chain_of_verification "Name some politicians born in New York City."

    # Show the draft, the verification Q&A, and the final verified answer
    python -m chain_of_verification "Who composed the four seasons?" --show-steps
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import verify
from .llm import DEFAULT_MODEL


def _print_steps(res) -> None:
    print("--- chain of verification ---")
    print("Draft answer:")
    print(f"  {res.baseline.strip()}")
    if res.verifications:
        print("Independent verifications:")
        for v in res.verifications:
            print(f"  Q: {v.question}")
            print(f"  A: {v.answer}")
    else:
        print("Independent verifications: (none planned)")
    print("-----------------------------")


def main() -> int:
    p = argparse.ArgumentParser(
        prog="chain_of_verification",
        description="Chain-of-Verification (Dhuliawala et al., 2023): draft, plan "
                    "verification questions, answer them independently, then revise.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("question", nargs="?", help="The question to answer.")
    p.add_argument("--max-questions", type=int, default=5,
                   help="Cap on verification questions (default: 5).")
    p.add_argument("--model", default=None, help=f"Model slug (default: {DEFAULT_MODEL}).")
    p.add_argument("--show-steps", action="store_true",
                   help="Print the draft and the independent verification Q&A.")
    args = p.parse_args()

    if not args.question:
        p.error("provide a question to answer")

    print(f"\nQuestion: {args.question}", file=sys.stderr)
    print(f"Model: {args.model or DEFAULT_MODEL}\n", file=sys.stderr, flush=True)

    res = verify(args.question, max_questions=args.max_questions, model=args.model)
    if args.show_steps:
        _print_steps(res)
    print("=" * 60)
    print(res.final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
