from abc import ABC, abstractmethod


class LLMProtector(ABC):
    """
    This class is an abstract class that represents the interface of the protector.
    """
    @abstractmethod
    def protect_call(self, system_instruction_template, system_input_variables, app_instruction, user_input_variables):
        """
        This method is used to protect the call.

        :param system_instruction_template:
        :param system_input_variables:
        :param app_instruction:
        :param user_input_variables:
        :return:
        """
        raise NotImplementedError()
