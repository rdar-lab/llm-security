import logging

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from llm.llm_manager import LLMManager
from llm.protectors.protector_utils import get_protector

_QUESTION_INSTRUCTION_WITH_DATA = 'You are a website reader. Answer a question about the content.'
_QUESTION_INSTRUCTION_REACT = 'You are a website reader. Answer a user question about the page.\nURL: {url}'

_logger = logging.getLogger(__name__)


def _get_use_rag(request):
    use_rag_str = request.GET.get('rag', 'false')
    use_embeddings = use_rag_str.lower() == 'true' or use_rag_str == '1'
    return use_embeddings


def _get_question(request):
    question = request.GET.get('question', '')
    if question is None or len(question) == 0:
        raise ValidationError('Invalid question')
    return question


def _get_site_url(request):
    site_url = request.GET.get('site_url', '')
    if site_url is None or len(site_url) == 0:
        raise ValidationError('Invalid site URL')
    return site_url


class AskQuestionOnSiteWithDataView(APIView):
    """
    Ask a question about a website with data (preloaded/RAG)
    """
    queryset = User.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        site_url = _get_site_url(request)
        question = _get_question(request)

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_WITH_DATA
        use_rag = _get_use_rag(request)

        answer = None
        parsed_answer = None
        error = None
        try:
            llm = LLMManager(protector=get_protector(request))
            answer = llm.answer_question_on_web_page_with_data(instruction, prompt_args,
                                                               rag=use_rag)
            parsed_answer = llm.parse_answer(answer)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": instruction,
            "prompt_args": prompt_args,
            "use_rag": use_rag,
            "answer": answer,
            "parsed_answer": parsed_answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})


class AskQuestionOnSiteReactView(APIView):
    """
    Ask a question about a website with React chain
    """
    queryset = User.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        site_url = _get_site_url(request)
        question = _get_question(request)

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_REACT

        answer = None
        parsed_answer = None
        error = None
        try:
            llm = LLMManager(protector=get_protector(request))
            answer = llm.answer_question_on_web_page_with_react(instruction, prompt_args)
            parsed_answer = llm.parse_answer(answer)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": instruction,
            "prompt_args": prompt_args,
            "answer": answer,
            "parsed_answer": parsed_answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})
