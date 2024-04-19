from django.urls import path

from .views import TransactionsView, TransactionSearchView

urlpatterns = [
    path('transaction/', TransactionsView.as_view(), name='transaction_list_create'),
    path('search/', TransactionSearchView.as_view(), name='transaction_search'),
]
