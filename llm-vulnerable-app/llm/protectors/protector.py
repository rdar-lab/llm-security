from abc import ABC, abstractmethod


class LLMProtector(ABC):
    @abstractmethod
    def protect_call(self, instruction_template, input_variables):
        raise NotImplementedError()
