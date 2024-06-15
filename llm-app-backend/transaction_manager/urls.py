from django.urls import path

from .views import TransactionsView, TransactionAskRATView, TransactionAskSQLView, TransactionAskPreloadedView

urlpatterns = [
    path('transaction/', TransactionsView.as_view(), name='transaction_list_create'),
    path('ask-rat/', TransactionAskRATView.as_view(), name='transaction_question'),
    path('ask-preloaded/', TransactionAskPreloadedView.as_view(), name='transaction_question_preloaded'),
    path('ask-sql/', TransactionAskSQLView.as_view(), name='transaction_search'),
]
