from rest_framework import status

from tests.test_base import TestBase
from transaction_manager.models import Transaction
from transaction_manager.serializers import TransactionSerializer


class PingViewTestCase(TestBase):
    def test_ping(self):
        response = self.client.get('/ping/')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
