#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys

from llm_project import startup_manager


def main():
    """Run administrative tasks."""
    if 'runserver' in sys.argv:
        startup_manager.init_app(env_type='dev')
    else:
        startup_manager.init_app(env_type='test')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
