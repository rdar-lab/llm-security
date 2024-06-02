import json
import logging

from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from llm.llm_helper import LLMHelper
from llm.protector_utils import get_protector
from .models import Transaction
from .serializers import TransactionSerializer

_logger = logging.getLogger(__name__)

_QUESTION_INSTRUCTION = \
    """
    You are a banker answering questions about transactions of the user.
    Only answer questions related to the table 'transaction_manager_transaction.
    Only answer questions related to the user (column = user_id) who is currently logged in.
    The user ID which is currently logged on is {user_id}.
    Important: You are only to return data. No updates should be made to the database.
    """

_SQL_INSTRUCTION = \
    """
    You are a banker answering questions about transactions of the user.
    Only answer questions related to the table 'transaction_manager_transaction.
    Only answer questions related to the user (column = user_id) who is currently logged in.
    The user ID which is currently logged on is {user_id}.
    Important: You are only to return data. No updates should be made to the database.
    DB Type is {db_type}.
    Here is the structure of the table:
    CREATE TABLE transaction_manager_transaction (
            id INTEGER NOT NULL, 
            amount DECIMAL NOT NULL, 
            description VARCHAR(255) NOT NULL, 
            date DATETIME NOT NULL, 
            created_at DATETIME NOT NULL, 
            updated_at DATETIME NOT NULL, 
            user_id INTEGER NOT NULL, 
            PRIMARY KEY (id), 
            FOREIGN KEY(user_id) REFERENCES auth_user (id)
    )
    """

_PRELOADED_INSTRUCTION = \
    """
    You are a banker answering questions about transactions of the user.
    Answer the question provided based on the information provided.
    """


def _get_search_text(request):
    search_text = request.GET.get('search_text', '')
    if search_text is None or len(search_text) == 0:
        raise ValidationError('Invalid search text')
    return search_text


class TransactionsView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # Only return the transactions of the logged-in user
        return Transaction.objects.filter(user=self.request.user)


# Question answering based on RAT (Retrieval Augmented Thoughts)
class TransactionAskView(APIView):
    queryset = Transaction.objects.none()

    def get(self, request):
        current_user_id = request.user.id
        search_text = _get_search_text(request)

        answer = None
        error = None

        prompt_args = {
            "query": search_text,
            "user_id": current_user_id
        }

        try:
            llm_helper = LLMHelper(protector=get_protector(request))
            # Use llm helper to answer the question
            answer = llm_helper.answer_question_on_db_with_rag(_QUESTION_INSTRUCTION, prompt_args)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": _QUESTION_INSTRUCTION,
            "prompt_args": prompt_args,
            "answer": answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})


# Question asking with data preloaded
class TransactionAskPreloadedView(APIView):
    queryset = Transaction.objects.none()

    def get(self, request):
        search_text = _get_search_text(request)

        prompt_args = None
        answer = None
        error = None

        try:
            data = json.dumps(
                list(Transaction.objects.filter(user=request.user).values()),
                default=lambda x: str(x)
            )
            prompt_args = {
                "data": data,
                "query": search_text,
            }

            llm_helper = LLMHelper(protector=get_protector(request))
            # Use llm helper to answer the question
            answer = llm_helper.answer_question(_PRELOADED_INSTRUCTION, prompt_args)
            answer = llm_helper.parse_answer(answer)
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)
        return JsonResponse({
            "prompt": _PRELOADED_INSTRUCTION,
            "prompt_args": prompt_args,
            "answer": answer,
            "error": error
        }, json_dumps_params={"default": lambda x: vars(x)})


# LLM as SQL generation engine
class TransactionSearchView(generics.ListAPIView):
    queryset = Transaction.objects.none()
    serializer_class = TransactionSerializer

    @staticmethod
    def get_queryset_by_sql(sql_query):
        # Filter the transactions using the SQL query
        transactions = Transaction.objects.raw(sql_query)

        return transactions

    def list(self, request, *args, **kwargs):
        prompt_args = None
        sql_query = None
        transactions = None
        error = None

        try:
            current_user_id = self.request.user.id
            search_text = _get_search_text(request)
            engine = settings.DATABASES['default']['ENGINE']
            prompt_args = {
                "query": search_text,
                "user_id": current_user_id,
                "db_type": engine
            }
            llm_helper = LLMHelper(protector=get_protector(request))
            sql_query = llm_helper.parse_answer(llm_helper.answer_question(_SQL_INSTRUCTION, prompt_args))
            queryset = self.filter_queryset(self.get_queryset_by_sql(sql_query))
            serializer = self.get_serializer(queryset, many=True)
            transactions = serializer.data
        except Exception as e:
            _logger.exception("Error while answering the question")
            error = repr(e)

        # Return the transactions and the summary
        return JsonResponse({
            'prompt': _SQL_INSTRUCTION,
            'prompt_args': prompt_args,
            'sql': sql_query,
            'transactions': transactions,
            'error': error
        })
