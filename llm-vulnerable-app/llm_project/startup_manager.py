import logging
import os


def _create_super_user():
    from django.contrib.auth.models import User
    from django.core.exceptions import ObjectDoesNotExist
    admin_user = os.environ.get('ADMIN_USER', 'admin')
    admin_password = os.environ.get('ADMIN_PASS', 'pass')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@test.com')

    try:
        User.objects.get(username=admin_user)
        logging.info(f"User {admin_user} already exists.")
    except ObjectDoesNotExist:
        try:
            User.objects.create_superuser(
                username=admin_user,
                email=admin_email,
                password=admin_password
            )
            logging.info(f"User {admin_user} created.")
        except Exception as exp:
            logging.exception(f"Failed to create user {admin_user}. Error={exp}")


def init_wsgi_app():
    logging.basicConfig(level=logging.INFO)
    from django.core.asgi import get_asgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    app = get_asgi_application()
    from django.core.management import call_command
    call_command('migrate')
    _create_super_user()
    return app


def init_asgi_app():
    logging.basicConfig(level=logging.INFO)
    from django.core.asgi import get_asgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    app = get_asgi_application()
    from django.core.management import call_command
    call_command('migrate')
    _create_super_user()
    return app
