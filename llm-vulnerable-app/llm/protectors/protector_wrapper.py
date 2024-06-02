from llm.protectors.protector import LLMProtector


class LLMProtectorWrapper(LLMProtector):

    def __init__(self, prefix='*** USER INPUT *** [\n', postfix='\n] *** END USER INPUT ***\n'):
        super().__init__()
        self.__prefix = prefix
        self.__postfix = postfix

    def protect_call(self, instruction_template, input_variables):
        query = input_variables["query"]
        query = self.__prefix + query + self.__postfix
        input_variables["query"] = query
        return instruction_template, input_variables
