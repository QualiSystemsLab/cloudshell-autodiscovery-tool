import unittest

import mock

from autodiscovery.exceptions import ReportableException
from autodiscovery.reports.base import AbstractEntry, AbstractReport


class TestAbstractReport(unittest.TestCase):
    def setUp(self):
        with mock.patch("autodiscovery.reports.base.AbstractEntry") as entry_class:

            class TestedClass(AbstractReport):
                @property
                def entry_class(self):
                    return entry_class

        self.entry_class = entry_class
        self.tested_instance = TestedClass()

    def test_add_entry(self):
        """Method should add entry into the entries list and return given entry."""
        entry = mock.MagicMock()
        self.entry_class.return_value = entry
        # act
        result = self.tested_instance.add_entry()
        # verify
        self.assertEqual(result, entry)
        self.assertIn(result, self.tested_instance._entries)
        self.entry_class.assert_called_once_with()

    def test_generate(self):
        """Method should raise exception if it wasn't implemented in the child class."""
        with self.assertRaises(NotImplementedError):
            self.tested_instance.generate()

    def parse_entries_from_file(self):
        """Method should raise exception if it wasn't implemented in the child class."""
        with self.assertRaises(NotImplementedError):
            self.tested_instance.parse_entries_from_file(report_file="report.xlsx")


class TestAbstractEntry(unittest.TestCase):
    def setUp(self):
        class TestedClass(AbstractEntry):
            pass

        self.entry = TestedClass(
            ip="test_ip", status=AbstractEntry.SUCCESS_STATUS, domain="Tets domain"
        )

    def test_enter_with_statement(self):
        """Check that with statement will return same entry."""
        with self.entry as entry:
            self.assertEqual(self.entry, entry)

    def test_exit_with_statement(self):
        """Check that entry status will be changed to the failed one."""
        with self.assertRaisesRegexp(Exception, "Test Exception"):
            with self.entry as entry:
                self.assertEqual(self.entry, entry)
                raise ReportableException("Test Exception")

        self.assertEqual(self.entry.status, AbstractEntry.FAILED_STATUS)
        self.assertEqual(self.entry.comment, "Test Exception")
