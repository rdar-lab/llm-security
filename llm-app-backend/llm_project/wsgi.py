"""
WSGI config for llm_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

from llm_project import startup_manager

application = startup_manager.init_app(env_type='prod', app_type='wsgi')


def create_app():
    return application
