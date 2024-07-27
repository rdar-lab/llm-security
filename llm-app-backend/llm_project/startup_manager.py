import logging
import os

from common.general_utils import get_project_root

app = None


def _load_env(env_type):
    """
    Load the environment variables from the .env file

    :param env_type:
    :return:
    """
    from dotenv import load_dotenv

    root_folder = get_project_root()
    if env_type == 'dev':
        env_file = root_folder + '/config/dev.env'
    elif env_type == 'test':
        env_file = root_folder + '/config/test.env'
    elif env_type == 'prod':
        env_file = root_folder + '/config/prod.env'
    else:
        raise ValueError(f"Invalid ENV_TYPE: {env_type}")

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"Env file not found: {env_file}")

    load_dotenv(env_file)


def _create_super_user():
    """
    Creates the superuser if it does not exist

    :return:
    """
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


def _init_logging():
    """
    Init the logging system

    :return:
    """
    from django.utils.log import configure_logging
    from django.conf import settings
    configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)


def _migrate():
    """
    Run DB migration
    :return:
    """
    from django.core.management import call_command
    call_command('migrate')


def _init_wsgi_app_inner():
    """
    Creates a wsgi application

    :return:
    """
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    app = get_wsgi_application()
    return app


def _init_asgi_app_inner():
    """
    Creates an asgi application

    :return:
    """
    from django.core.asgi import get_asgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')
    app = get_asgi_application()
    return app


def init_app(env_type, app_type='wsgi'):
    """
    Hook for init and creation of the application

    :param env_type:
    :param app_type:
    :return:
    """
    global app
    if app is None:
        _load_env(env_type)
        if app_type == 'wsgi':
            app = _init_wsgi_app_inner()
        elif app_type == 'asgi':
            app = _init_asgi_app_inner()
        else:
            raise ValueError(f"Invalid app type: {app_type}")
        _init_logging()
        logger = logging.getLogger(__name__)
        logger.info(f"Init app. ENV_TYPE={env_type}, APP_TYPE={app_type}")
        _migrate()
        _create_super_user()
    return app
