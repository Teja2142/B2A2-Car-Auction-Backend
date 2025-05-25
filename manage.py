#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    port = os.getenv('PORT', '8000')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_auction.settings')
    os.environ.setdefault('DJANGO_ALLOWED_HOSTS', '127.0.0.1')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Only run 'runserver' when explicitly requested
    execute_from_command_line(sys.argv)
    # execute_from_command_line([sys.argv[0], 'runserver', f'0.0.0.0:{port}'])
    

if __name__ == '__main__':
    main()
