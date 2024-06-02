import logging

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from llm.llm_manager import LLMManager
from llm.protectors.protector_utils import get_protector
from transaction_manager.models import Transaction

_QUESTION_INSTRUCTION_RETRIEVER = 'You are a website reader. Answer a question about the content.'
_QUESTION_INSTRUCTION_RAG = 'You are a website reader. Answer a user question about the page.\nURL: {url}'

_logger = logging.getLogger(__name__)


def _get_use_embedding(request):
    use_embeddings_str = request.GET.get('use_embeddings', 'false')
    use_embeddings = use_embeddings_str.lower() == 'true' or use_embeddings_str == '1'
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


class AskQuestionOnSiteRetrieverView(APIView):
    queryset = Transaction.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        site_url = _get_site_url(request)
        question = _get_question(request)

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_RETRIEVER
        use_embeddings = _get_use_embedding(request)

        answer = None
        error = None
        try:
            llm = LLMManager(protector=get_protector(request))
            answer = llm.answer_question_on_web_page_with_retriever(instruction, prompt_args,
                                                                           embedding=use_embeddings)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": instruction,
            "prompt_args": prompt_args,
            "use_embeddings": use_embeddings,
            "answer": answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})


class AskQuestionOnSiteRagView(APIView):
    queryset = Transaction.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        site_url = _get_site_url(request)
        question = _get_question(request)

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_RAG

        answer = None
        error = None
        try:
            llm = LLMManager(protector=get_protector(request))
            answer = llm.answer_question_on_web_page_with_rag(instruction, prompt_args)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": instruction,
            "prompt_args": prompt_args,
            "answer": answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})
