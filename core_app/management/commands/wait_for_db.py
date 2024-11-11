"""
Django command to wait for the database to be available.
"""

from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
import time


class Command(BaseCommand):
    """
    Django command to wait for the database.
    """

    def handle(self, *args, **options):
        """
        Entry point for command.
        """

        self.stdout.write("Waiting for database...")

        while True:
            try:
                self.check(databases=["default", ])
            except (Psycopg2OpError, OperationalError):
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)
            else:
                break
        
        self.stdout.write(self.style.SUCCESS("Database available!"))
