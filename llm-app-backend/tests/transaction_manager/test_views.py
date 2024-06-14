from rest_framework import status

from tests.test_base import TestBase
from transaction_manager.models import Transaction
from transaction_manager.serializers import TransactionSerializer


class TransactionsViewTestCase(TestBase):
    def test_get_all_transactions(self):
        response = self.client.get('/api/transaction_manager/transaction/')
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        self.assertEqual(serializer.data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_create_transaction(self):
        data = {
            'amount': 100,
            'description': 'test Description',
            # Add all necessary fields here
        }
        response = self.client.post('/api/transaction_manager/transaction/', data=data)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
