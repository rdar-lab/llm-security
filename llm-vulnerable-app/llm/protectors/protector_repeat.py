import logging

from llm.protectors.protector import LLMProtector

_logger = logging.getLogger(__name__)


class LLMProtectorRepeat(LLMProtector):

    def __init__(self, repeat=1):
        super().__init__()
        self.__repeat = repeat

    def protect_call(self, system_instruction_template, system_input_variables, app_instruction, user_input_variables):
        if 'instruction' in system_input_variables:
            system_instruction_template = system_instruction_template + '\nReminder: {instruction}'
        else:
            _logger.warning("Instruction template does not contain 'instruction' variable - Ignoring it")

        return system_instruction_template, system_input_variables
