import unittest
from unittest import IsolatedAsyncioTestCase, TestCase

from google.auth.exceptions import DefaultCredentialsError

from async_translate.async_translate import AsyncTranslate
from async_translate.errors import TranslatorException
from async_translate.providers.azure import Azure
from async_translate.providers.google import Google


class ProviderTests(TestCase):
    def test_azure_no_keys(self):
        """Ensure Error is raised when not providing any keys"""
        with self.assertRaises(TranslatorException):
            Azure(api_keys=[])

    def test_google_no_credentials(self):
        """Ensure Error is raised when not providing any credentials"""
        with self.assertRaises(DefaultCredentialsError):
            Google()


if __name__ == '__main__':
    unittest.main()
