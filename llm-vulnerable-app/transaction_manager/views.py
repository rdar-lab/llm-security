from django.http import JsonResponse
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from .llm_helper import LLmHelper
from .models import Transaction
from .serializers import TransactionSerializer

_INSTRUCTION = \
    ("Only answer questions related to the table 'transaction_manager_transaction'.\n"
     "Only answer questions related to the user (column = user_id) who is currently logged in.\n"
     'The user ID which is currently logged on is {user_id}.\n'
     'Important: You are only to return data. No updates should be made to the database.\n'
     '{query}')


class TransactionsView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # Only return the transactions of the logged-in user
        return Transaction.objects.filter(user=self.request.user)


class TransactionSearchView(APIView):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.none()

    def get(self, request, *args, **kwargs):
        current_user_id = request.user.id

        search_text = self.__get_search_text()

        llm_helper = LLmHelper()
        # Use llm helper to answer the question
        answer = llm_helper.answer_question_on_db(_INSTRUCTION, {
            "query": search_text,
            "user_id": current_user_id
        })
        #
        # if "output" in answer:
        #     answer = answer["output"]

        return JsonResponse({"answer": answer}, json_dumps_params={"default": lambda x: vars(x)})

    def __get_search_text(self):
        search_text = self.request.GET.get('search_text', '')
        if search_text is None or len(search_text) == 0:
            raise ValidationError('Invalid search text')
        return search_text
