from django.urls import path

from .views import TransactionsView, TransactionAskReactView, TransactionAskGenSQLView, TransactionAskPreloadedView

urlpatterns = [
    path('transaction/', TransactionsView.as_view(), name='transaction_list_create'),
    path('ask-react/', TransactionAskReactView.as_view(), name='transaction_ask_react'),
    path('ask-preloaded/', TransactionAskPreloadedView.as_view(), name='transaction_ask_preloaded'),
    path('ask-sql/', TransactionAskGenSQLView.as_view(), name='transaction_ask_sql'),
]
