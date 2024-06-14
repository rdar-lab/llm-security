from django.urls import path

from .views import TransactionsView, TransactionAskView, TransactionSearchView, TransactionAskPreloadedView

urlpatterns = [
    path('transaction/', TransactionsView.as_view(), name='transaction_list_create'),
    path('ask/', TransactionAskView.as_view(), name='transaction_question'),
    path('ask-preloaded/', TransactionAskPreloadedView.as_view(), name='transaction_question_preloaded'),
    path('search/', TransactionSearchView.as_view(), name='transaction_search'),
]
