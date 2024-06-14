import logging

from llm.protectors.protector import LLMProtector

_logger = logging.getLogger(__name__)


class LLMProtectorWrapper(LLMProtector):

    def __init__(
            self,
            user_input_prefix='*** START USER INPUT *** [\n',
            user_input_postfix='\n] *** END USER INPUT ***\n',
            data_prefix='*** START DATA *** [\n',
            data_postfix='\n] *** END DATA ***\n'

    ):
        super().__init__()
        self.__user_input_prefix = user_input_prefix
        self.__user_input_postfix = user_input_postfix
        self.__data_prefix = data_prefix
        self.__data_postfix = data_postfix

    def protect_call(self, system_instruction_template, system_input_variables, app_instruction, user_input_variables):
        if 'query' in system_input_variables:
            query = system_input_variables["query"]
            query = f'{self.__user_input_prefix}{query}{self.__user_input_postfix}'
            system_input_variables["query"] = query
        else:
            _logger.warning("Instruction template does not contain 'query' variable - Ignoring it")

        if 'data' in system_input_variables:
            data = system_input_variables["data"]
            data = f'{self.__data_prefix}{data}{self.__data_postfix}'
            system_input_variables["data"] = data

        return system_instruction_template, system_input_variables
