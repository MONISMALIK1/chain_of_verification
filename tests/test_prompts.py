"""Prompt template sanity checks (placeholders + routing markers)."""

import unittest

from chain_of_verification.prompts import (BASELINE_PROMPT, PLAN_PROMPT,
                                           REVISE_PROMPT, VERIFY_PROMPT)


class PromptTests(unittest.TestCase):
    def test_placeholders(self):
        self.assertIn("{question}", BASELINE_PROMPT)
        self.assertIn("{question}", PLAN_PROMPT)
        self.assertIn("{baseline}", PLAN_PROMPT)
        self.assertIn("{question}", VERIFY_PROMPT)
        self.assertIn("{question}", REVISE_PROMPT)
        self.assertIn("{baseline}", REVISE_PROMPT)
        self.assertIn("{verifications}", REVISE_PROMPT)

    def test_routing_markers_are_distinct(self):
        markers = [
            "Answer the following question as best you can",  # baseline
            "fact-checking a draft answer",                   # plan
            "Answer this single factual question",            # verify
            "fact-checked it with independent verification",  # revise
        ]
        prompts = [BASELINE_PROMPT, PLAN_PROMPT, VERIFY_PROMPT, REVISE_PROMPT]
        for marker, own in zip(markers, prompts):
            self.assertIn(marker, own)
            # the marker must appear in exactly one of the four prompts
            self.assertEqual(sum(marker in p for p in prompts), 1, marker)


if __name__ == "__main__":
    unittest.main()
