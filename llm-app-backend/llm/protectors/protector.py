from abc import ABC, abstractmethod


class LLMProtector(ABC):
    @abstractmethod
    def protect_call(self, system_instruction_template, system_input_variables, app_instruction, user_input_variables):
        raise NotImplementedError()
