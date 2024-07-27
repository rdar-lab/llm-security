import copy
import itertools
import logging
import random
from itertools import combinations

from llm.llm_manager import LLMManager
from llm.protectors.protector import LLMProtector
from llm.protectors.protector_with_llm import LLMProtectorWithLLM

_logger = logging.getLogger(__name__)


class LLMProtectorEraseAndCheck(LLMProtector):
    """
    A protector that uses the erase-and-check defense to protect against attacks
    """

    def __init__(self, mode):
        super().__init__()
        self._llm = LLMManager()
        self.__mode = mode

    def protect_call(self, system_instruction_template, system_input_variables, app_instruction, user_input_variables):
        if 'query' not in user_input_variables:
            _logger.warning("User input does not contain 'query' variable - Will not protect it")
            return system_instruction_template, system_input_variables

        is_safe = LLMProtectorEraseAndCheck._erase_and_check(
            llm=self._llm,
            app_instruction=app_instruction,
            user_input_variables=user_input_variables,
            mode=self.__mode)
        if not is_safe:
            _logger.warning(f"The instruction is dangerous - Ignoring it")
            raise Exception(f"Instruction flagged")
        else:
            return system_instruction_template, system_input_variables

    @staticmethod
    def _is_safe(llm, app_instruction, user_input_variables, queries_variations, majority=False):
        """
        Check if any of the queries are safe or not.
        """
        _logger.info(f'Checking if queries are safe. prompts={queries_variations}')
        results = []
        for query in queries_variations:
            cp_vars = copy.copy(user_input_variables)
            cp_vars['query'] = query
            is_safe, _ = LLMProtectorWithLLM.is_safe(llm, app_instruction, cp_vars)
            results.append(is_safe)

        _logger.info(f'Queries safe results: {results}')

        if not majority:
            return all(results)
        else:
            return sum(results) > len(results) / 2

    @staticmethod
    def _erase_and_check(llm: LLMManager, app_instruction, user_input_variables, max_erase=20, num_adv=2,
                         mode="erase-and-check-suffix", majority=False, max_prompts=5):
        prompts_to_test = LLMProtectorEraseAndCheck._generate_prompts(llm, user_input_variables, mode, max_erase,
                                                                      num_adv, max_prompts)

        # Check if any of the erased strings is harmful
        return LLMProtectorEraseAndCheck._is_safe(llm, app_instruction, user_input_variables,
                                                  prompts_to_test, majority=majority)

    @staticmethod
    def _generate_prompts(llm, user_input_variables, mode, max_erase, num_adv, max_prompts):
        if mode == "erase-and-check-suffix":
            prompt_list = LLMProtectorEraseAndCheck._erase_and_check_suffix(llm, user_input_variables,
                                                                            max_erase=max_erase)
        elif mode == "erase-and-check-infusion":
            prompt_list = LLMProtectorEraseAndCheck._erase_and_check_infusion(llm, user_input_variables,
                                                                              max_erase=max_erase)
        elif mode == "erase-and-check-insertion":
            prompt_list = LLMProtectorEraseAndCheck._erase_and_check_insertion(llm, user_input_variables,
                                                                               max_erase=max_erase, num_adv=num_adv)
        else:
            raise ValueError("Invalid mode: " + mode)

        _logger.info(f"Performing {mode} - Generated {len(prompt_list)} prompts to test.")
        prompts_to_test = LLMProtectorEraseAndCheck._randomized_prompts(prompt_list, max_prompts)
        return prompts_to_test

    @staticmethod
    def _erase_and_check_suffix(llm: LLMManager, user_input_variables, max_erase):
        """
        Erase the prompt one token at a time from the end and check if any of the generated substrings is harmful.
        """

        prompt, prompt_length, prompt_tokens = LLMProtectorEraseAndCheck.__extract_prompts(llm, user_input_variables)

        # Erase the prompt one token at a time from the end
        prompt_list = [prompt]

        for i in range(min(max_erase, prompt_length)):
            erased_prompt_tokens = prompt_tokens[:-(i + 1)]
            erased_prompt = llm.detokenize(erased_prompt_tokens)
            prompt_list.append(erased_prompt)

        return prompt_list

    @staticmethod
    def __extract_prompts(llm, user_input_variables):
        prompt = user_input_variables['query']
        # Tokenize the prompt
        prompt_tokens = llm.tokenize(prompt)
        prompt_length = len(prompt_tokens)
        return prompt, prompt_length, prompt_tokens

    @staticmethod
    def _randomized_prompts(prompt_list, max_prompts):
        prompt_list = [prompt for prompt in prompt_list if prompt is not None and len(prompt) > 0]

        if len(prompt_list) > max_prompts:
            prompts_to_test = prompt_list[0:1] + random.sample(prompt_list[1:], max_prompts - 1)
        else:
            prompts_to_test = prompt_list
        return prompts_to_test

    @staticmethod
    def _erase_and_check_infusion(llm: LLMManager, user_input_variables, max_erase):
        """
        Erase subsets of the prompt and check if any of the generated substrings is harmful.
        This method is a certified defense against attacks where adversarial tokens could be inserted anywhere in the
        prompt, not necessarily in a contiguous block.
        """

        prompt, prompt_length, prompt_tokens = LLMProtectorEraseAndCheck.__extract_prompts(llm, user_input_variables)

        prompt_list = [prompt]
        # for i in range(min(max_erase, prompt_length - min_length)):
        for i in range(min(max_erase, prompt_length)):
            # Mark erase locations
            erase_locations = list(combinations(range(prompt_length), i + 1))
            for location in erase_locations:
                erased_prompt_tokens = LLMProtectorEraseAndCheck._delete_by_indices(prompt_tokens, location)
                erased_prompt = llm.detokenize(erased_prompt_tokens)
                prompt_list.append(erased_prompt)

        return prompt_list

    @staticmethod
    def _delete_by_indices(data_list, indices):
        """
        Delete elements from a list by their indices.
        Args:
            data_list: The list to delete from.
            indices: The indices to delete.
        Returns:
            The list with the elements at the given indices deleted.
        """
        data_list = data_list.copy()
        # Sort indices in descending order to ensure deletion doesn't affect subsequent indices
        for index in sorted(indices, reverse=True):
            del data_list[index]
        return data_list

    @staticmethod
    def _erase_and_check_insertion(llm: LLMManager, user_input_variables, max_erase, num_adv):
        """
        A generalized version of erase_and_check() that can defend against multiple adversarial prompts inserted into the prompt
        where each adversarial prompt is a contiguous block of adversarial tokens.
        """

        prompt, prompt_length, prompt_tokens = LLMProtectorEraseAndCheck.__extract_prompts(llm, user_input_variables)

        prompt_set = set()

        # All possible gap and num_erase values
        args = []
        for k in range(num_adv):
            args.append(range(prompt_length))
            args.append(range(max_erase + 1))

        # Iterate over all possible combinations of gap and num_erase values
        for combination in itertools.product(*args):

            erase_locations = []
            start = 0
            end = 0
            for i in range(len(combination) // 2):
                start = end + combination[(2 * i)]
                end = start + combination[(2 * i) + 1]
                if start >= prompt_length or end > prompt_length:
                    erase_locations = []
                    break
                erase_locations.extend(range(start, end))

            if len(erase_locations) == 0 or len(erase_locations) > prompt_length:
                continue

            erased_prompt_tokens = LLMProtectorEraseAndCheck._delete_by_indices(prompt_tokens, erase_locations)
            erased_prompt = llm.detokenize(erased_prompt_tokens)
            prompt_set.add(erased_prompt)

        if prompt in prompt_set:
            prompt_set.remove(prompt)

        prompt_list = [prompt] + list(prompt_set)
        return prompt_list
