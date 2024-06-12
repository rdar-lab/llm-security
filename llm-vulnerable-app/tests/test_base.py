import logging
import os
from abc import ABC

from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.test import TestCase
from django.contrib.auth.models import User

is_initialized = False


def _init():
    global is_initialized
    if not is_initialized:
        call_command('migrate')
        User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='password'
        )
        is_initialized = True


class TestBase(TestCase, ABC):
    _application = None
    _client = None

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(level=logging.DEBUG)
        _init()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='password')
