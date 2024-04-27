from django.urls import path

from .views import TransactionsView, TransactionAskView, TransactionSearchView

urlpatterns = [
    path('transaction/', TransactionsView.as_view(), name='transaction_list_create'),
    path('ask/', TransactionAskView.as_view(), name='transaction_question'),
    path('search/', TransactionSearchView.as_view(), name='transaction_search'),
]
