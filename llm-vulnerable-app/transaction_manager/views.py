from django.conf import settings
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from .llm_helper import LLmHelper
from .models import Transaction
from .serializers import TransactionSerializer

_QUESTION_INSTRUCTION = \
    """
    Only answer questions related to the table 'transaction_manager_transaction.
    Only answer questions related to the user (column = user_id) who is currently logged in.
    The user ID which is currently logged on is {user_id}.
    Important: You are only to return data. No updates should be made to the database.
    {query}
    """

_SQL_INSTRUCTION = \
    """
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
    {query}
)
    """


class TransactionsView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # Only return the transactions of the logged-in user
        return Transaction.objects.filter(user=self.request.user)


# Question answering based on RAT (Retrieval Augmented Thoughts)
class TransactionAskView(APIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.none()

    def get(self, request, *args, **kwargs):
        current_user_id = request.user.id

        search_text = self.__get_search_text()

        llm_helper = LLmHelper()
        # Use llm helper to answer the question
        answer = llm_helper.answer_question_on_db(_QUESTION_INSTRUCTION, {
            "query": search_text,
            "user_id": current_user_id
        })

        return JsonResponse({"answer": answer}, json_dumps_params={"default": lambda x: vars(x)})

    def __get_search_text(self):
        search_text = self.request.GET.get('search_text', '')
        if search_text is None or len(search_text) == 0:
            raise ValidationError('Invalid search text')
        return search_text


# LLM as SQL generation engine
class TransactionSearchView(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self, sql_query=None):
        if sql_query is None:
            sql_query = self._calc_sql_query()

        # Filter the transactions using the SQL query
        transactions = Transaction.objects.raw(sql_query)

        return transactions

    def _calc_sql_query(self):
        current_user_id = self.request.user.id
        search_text = self.__get_search_text()
        engine = settings.DATABASES['default']['ENGINE']
        llm_helper = LLmHelper()
        llm_answer = llm_helper.answer_question(_SQL_INSTRUCTION, {
            "query": search_text,
            "user_id": current_user_id,
            "db_type": engine
        })
        sql_query = llm_helper.parse_answer(llm_answer)
        return sql_query

    def __get_search_text(self):
        search_text = self.request.GET.get('search_text', '')
        if search_text is None or len(search_text) == 0:
            raise ValidationError('Invalid search text')
        return search_text

    def list(self, request, *args, **kwargs):
        sql_query = self._calc_sql_query()
        try:
            queryset = self.filter_queryset(self.get_queryset(sql_query))
            serializer = self.get_serializer(queryset, many=True)
            transactions = serializer.data
            error = None
        except Exception as e:
            transactions = []
            error = repr(e)

        # Return the transactions and the summary
        return JsonResponse({
            'sql': sql_query,
            'transactions': transactions,
            'error': error
        })
