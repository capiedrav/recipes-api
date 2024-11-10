from unittest.mock import patch
from psycopg2 import OperationalError as Pyscopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core_app.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):

    def test_wait_for_db_when_db_is_ready(self, patched_check):
        """
        Test waiting for database when database is ready
        for connections.
        """

        patched_check.return_value = True # mock check function returns True 

        call_command("wait_for_db") # call function

        # check the function is called with the default database
        patched_check.assert_called_once_with(database=["default", ])

    @patch("time.sleep")
    def test_wait_for_db_when_db_is_not_ready(self, patched_sleep, patched_check):
        """
        Test waiting for the database when the database is not ready for connections.
        """

        # mock check function raises 2 Pyscopg2Errors, 3 OperationalErrors, and finally it returns True
        patched_check.side_effect = [Pyscopg2Error] * 2 + [OperationalError] * 3 + [True]

        call_command("wait_for_db") # call function

        # verify check function was called six times
        self.assertEqual(patched_check.call_count, 6)

        # check the function is called with the default database
        patched_check.assert_called_with(database=["default", ])
