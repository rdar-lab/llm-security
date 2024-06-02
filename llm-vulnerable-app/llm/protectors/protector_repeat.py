import logging

from llm.protectors.protector import LLMProtector

_logger = logging.getLogger(__name__)


class LLMProtectorRepeat(LLMProtector):

    def __init__(self, repeat=1):
        super().__init__()
        self.__repeat = repeat

    def protect_call(self, instruction_template, input_variables):
        if 'instruction' in instruction_template:
            instruction_template = instruction_template + '\nReminder: {instruction}'
        else:
            _logger.warning("Instruction template does not contain 'instruction' variable - Ignoring it")

        return instruction_template, input_variables
