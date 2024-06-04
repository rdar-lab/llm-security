import logging

from llm.protectors.protector import LLMProtector

_logger = logging.getLogger(__name__)


class LLMProtectorWrapper(LLMProtector):

    def __init__(self, prefix='*** USER INPUT *** [\n', postfix='\n] *** END USER INPUT ***\n'):
        super().__init__()
        self.__prefix = prefix
        self.__postfix = postfix

    def protect_call(self, system_instruction_template, system_input_variables, user_instruction, user_input_variables):
        if 'query' in system_input_variables:
            query = system_input_variables["query"]
            query = self.__prefix + query + self.__postfix
            system_input_variables["query"] = query
        else:
            _logger.warning("Instruction template does not contain 'query' variable - Ignoring it")
        return system_instruction_template, system_input_variables
