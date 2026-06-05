"""The CoVe pipeline end to end, with a scripted model (offline).

Proves the behaviours the paper describes: the draft is fact-checked by planned
questions, each verification is answered *in isolation* (the factored variant — its
prompt never contains the draft or the other questions), and the revision is built
from those verified answers.
"""

import unittest

from chain_of_verification.core import CoVeResult, parse_questions, verify


class FactoredPipelineTests(unittest.TestCase):
    def setUp(self):
        self.seen = []

        def fake(prompt, model=None):
            self.seen.append(prompt)
            if "Answer the following question as best you can" in prompt:
                return "1. Donald Trump\n2. Hillary Clinton\n3. Franklin D. Roosevelt"
            if "fact-checking a draft answer" in prompt:
                return ("Where was Donald Trump born?\n"
                        "Where was Hillary Clinton born?\n"
                        "Where was Franklin D. Roosevelt born?")
            if "Answer this single factual question" in prompt:
                if "Trump" in prompt:
                    return "New York City"
                if "Clinton" in prompt:
                    return "Chicago, Illinois"
                if "Roosevelt" in prompt:
                    return "Hyde Park, New York"
                return "unsure"
            if "fact-checked it with independent verification" in prompt:
                return "Donald Trump was born in New York City."
            return "?"

        self.fake = fake

    def test_collects_independent_verifications(self):
        res = verify("Name politicians born in New York City.", chat_fn=self.fake)
        self.assertIsInstance(res, CoVeResult)
        self.assertEqual(len(res.verifications), 3)
        self.assertEqual(res.verifications[1].question, "Where was Hillary Clinton born?")
        self.assertEqual(res.verifications[1].answer, "Chicago, Illinois")
        self.assertIn("Trump", res.final)
        self.assertIn("Trump", res.baseline)

    def test_verifications_are_factored(self):
        verify("Name politicians born in New York City.", chat_fn=self.fake)
        verify_prompts = [p for p in self.seen if "Answer this single factual question" in p]
        self.assertEqual(len(verify_prompts), 3)
        trump_prompt = next(p for p in verify_prompts if "Trump" in p)
        # Isolated: the draft and the *other* entities must not leak in.
        self.assertNotIn("Clinton", trump_prompt)
        self.assertNotIn("Roosevelt", trump_prompt)
        self.assertNotIn("Draft answer", trump_prompt)

    def test_max_questions_caps_verifications(self):
        res = verify("Name politicians born in New York City.", max_questions=2,
                     chat_fn=self.fake)
        self.assertEqual(len(res.verifications), 2)


class NoQuestionsTests(unittest.TestCase):
    def test_baseline_stands_when_nothing_to_verify(self):
        def fake(prompt, model=None):
            if "Answer the following question as best you can" in prompt:
                return "42"
            if "fact-checking a draft answer" in prompt:
                return ""  # the planner proposes no verification questions
            return "?"

        res = verify("What is 6 times 7?", chat_fn=fake)
        self.assertEqual(res.final, "42")
        self.assertEqual(res.baseline, "42")
        self.assertEqual(res.verifications, [])


class ParseQuestionsTests(unittest.TestCase):
    def test_numbered_and_bulleted(self):
        text = "1. Where was X born?\n2) When did Y die?\n- What is Z?\n* Another one"
        self.assertEqual(parse_questions(text),
                         ["Where was X born?", "When did Y die?", "What is Z?", "Another one"])

    def test_skips_blank_and_header_lines(self):
        text = "Verification questions:\n\nWhere was X born?\n   \nWhat is Y?"
        self.assertEqual(parse_questions(text), ["Where was X born?", "What is Y?"])


if __name__ == "__main__":
    unittest.main()
