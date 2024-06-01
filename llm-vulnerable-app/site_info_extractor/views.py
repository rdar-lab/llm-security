import logging

from django.http import JsonResponse
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from common.llm_helper import LLmHelper
from transaction_manager.models import Transaction

_QUESTION_INSTRUCTION_RETRIEVER = 'You are a website reader. Answer a question about the content.\n{query}'
_QUESTION_INSTRUCTION_RAG = 'You are a website reader. Answer a question about the page.\nURL: {url}\n{query}'

_logger = logging.getLogger(__name__)


class AskQuestionOnSiteRetrieverView(APIView):
    queryset = Transaction.objects.none()

    # noinspection PyMethodMayBeStatic
    def get(self, request):
        site_url = request.GET.get('site_url', '')
        if site_url is None or len(site_url) == 0:
            raise ValidationError('Invalid site URL')

        question = request.GET.get('question', '')
        if question is None or len(question) == 0:
            raise ValidationError('Invalid question')

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_RETRIEVER
        use_embeddings_str = request.GET.get('use_embeddings', 'false')
        use_embeddings = use_embeddings_str.lower() == 'true' or use_embeddings_str == '1'

        answer = None
        error = None
        try:
            llm_helper = LLmHelper()
            answer = llm_helper.answer_question_on_web_page_with_retriever(instruction, prompt_args,
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
        site_url = request.GET.get('site_url', '')
        if site_url is None or len(site_url) == 0:
            raise ValidationError('Invalid site URL')

        question = request.GET.get('question', '')
        if question is None or len(question) == 0:
            raise ValidationError('Invalid question')

        prompt_args = {"url": site_url, "query": question}
        instruction = _QUESTION_INSTRUCTION_RAG

        answer = None
        error = None
        try:
            llm_helper = LLmHelper()
            answer = llm_helper.answer_question_on_web_page_with_rag(instruction, prompt_args)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": instruction,
            "prompt_args": prompt_args,
            "answer": answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})
