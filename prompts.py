"""The four CoVe prompts (Dhuliawala et al., 2023).

Draft -> plan verification questions -> answer each *independently* -> revise. The
independence in step 3 is the crux: each verification question is answered in
isolation (the ``factored`` variant), so a hallucination in the draft can't prime
its own confirmation. The markers in each prompt's first sentence let the offline
tests route a scripted model without ambiguity.
"""

# (i) Draft an initial answer.
BASELINE_PROMPT = """Answer the following question as best you can. Be specific and concise.

Question: {question}

Answer:"""

# (ii) Plan verification questions that fact-check the draft's claims.
PLAN_PROMPT = """You are fact-checking a draft answer. Write a list of verification questions \
that would check whether the factual claims in the draft are correct. Each question must be \
answerable on its own, in isolation, without the draft. Write one question per line, with no \
numbering and no commentary.

Question: {question}

Draft answer:
{baseline}

Verification questions:"""

# (iii) Answer ONE verification question, in isolation (the factored variant).
VERIFY_PROMPT = """Answer this single factual question accurately and concisely. If you are not \
certain, say "unsure". Answer only this question and do not assume any other context.

Question: {question}

Answer:"""

# (iv) Revise the draft using the verified facts.
REVISE_PROMPT = """You drafted an answer, then fact-checked it with independent verification \
questions and their answers. Write a final answer to the original question that keeps only the \
claims the verifications support, and corrects or drops anything they contradict.

Original question: {question}

Draft answer:
{baseline}

Verification results:
{verifications}

Final verified answer:"""

__all__ = ["BASELINE_PROMPT", "PLAN_PROMPT", "VERIFY_PROMPT", "REVISE_PROMPT"]
