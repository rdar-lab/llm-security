import logging

from llm.llm_protectors import LLMProtectorWithLLM, LLMProtectorWrapper, LLMProtectorRepeat

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

    _logger.warning("Invalid protector: {}".format(protector))
    return None
