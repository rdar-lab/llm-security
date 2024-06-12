from unittest.mock import patch

from llm.llm_manager import LLMManager
from tests.test_base import TestBase


class LLMTokenizationTester(TestBase):
    @patch('llm.llm_manager.LLMManager._init_llm')
    def test_tokenization(self, init_llm_mock):
        init_llm_mock.return_value = None
        llm = LLMManager()
        tokens = llm.tokenize("Hello, how are you?")

        self.assertTrue(isinstance(tokens, list))

        back_to_orig = llm.detokenize(tokens)
        self.assertEqual(
            "Hello, how are you?",
            back_to_orig
        )
