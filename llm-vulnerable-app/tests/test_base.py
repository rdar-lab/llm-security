from abc import ABC

from django.test import TestCase

from llm_project import startup_manager

application = startup_manager.init_app(env_type='test')


class TestBase(TestCase, ABC):
    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='pass')
