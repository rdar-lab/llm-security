import logging

from llm.protectors.protector_erase_and_check import LLMProtectorEraseAndCheck
from llm.protectors.protector_repeat import LLMProtectorRepeat
from llm.protectors.protector_wrapper import LLMProtectorWrapper
from llm.protectors.protector_with_llm import LLMProtectorWithLLM

_logger = logging.getLogger(__name__)


def get_protector(request):
    """
    Get the protector based on the request

    :param request:
    :return:
    """
    protector = request.GET.get('protector', '')
    if protector is None or len(protector) == 0:
        return None

    if protector == 'none':
        return None

    if protector == 'llm':
        return LLMProtectorWithLLM()

    if protector == 'wrap':
        return LLMProtectorWrapper()

    if protector == 'repeat':
        return LLMProtectorRepeat()

    if 'erase-and-check' in protector:
        return LLMProtectorEraseAndCheck(mode=protector)

    raise Exception("Invalid protector: {}".format(protector))
