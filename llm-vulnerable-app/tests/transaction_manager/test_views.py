from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from llm_project.transaction_manager.models import Transaction
from llm_project.transaction_manager.serializers import TransactionSerializer


class TransactionsViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.list_url = reverse('transaction_manager:transaction_list')

    def test_get_all_transactions(self):
        response = self.client.get(self.list_url)
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_transaction(self):
        data = {
            'field1': 'value1',
            'field2': 'value2',
            # Add all necessary fields here
        }
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
