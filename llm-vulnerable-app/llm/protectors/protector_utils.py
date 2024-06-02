import logging

from llm.protectors.protector_repeat import LLMProtectorRepeat
from llm.protectors.protector_wrapper import LLMProtectorWrapper
from llm.protectors.protector_with_llm import LLMProtectorWithLLM

_logger = logging.getLogger(__name__)


def get_protector(request):
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

    raise Exception("Invalid protector: {}".format(protector))
