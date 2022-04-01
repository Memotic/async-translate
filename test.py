"""
Async Translate Unit Tests (in progress)
Create a file named testCreds.py with the following structure
```py
azure_keys = ['KEYS']
google_parent = ""
google_credentials = {
    "type": "",
    "project_id": "",
    "private_key_id": "",
    "private_key": "",
    "client_email": "",
    "client_id": "",
    "auth_uri": "",
    "token_uri": "",
    "auth_provider_x509_cert_url": "",
    "client_x509_cert_url": ""
}

```
"""
import unittest
from unittest import TestCase, IsolatedAsyncioTestCase

from google.auth.exceptions import DefaultCredentialsError

import testCreds
from async_translate import AsyncTranslate
from async_translate.providers.azure import Azure
from async_translate.providers.azure.errors import NoAPIKeys
from async_translate.providers.google import Google


class ProviderTests(TestCase):
    def test_azure_no_keys(self):
        """Ensure Error is raised when not providing any keys"""
        with self.assertRaises(NoAPIKeys):
            Azure(api_keys=[])

    def test_google_no_credentials(self):
        """Ensure Error is raised when not providing any credentials"""
        with self.assertRaises(DefaultCredentialsError):
            Google()


class AsyncTranslateTests(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.translator = AsyncTranslate()

    # noinspection PyMethodMayBeStatic
    def test_setup(self):
        try:
            import testCreds
        except ModuleNotFoundError:
            print(
                "Please create testCreds.py and populate it with the variables detailed in the docstring of this file.")
            raise

    async def asyncTearDown(self) -> None:
        await self.translator.close()

    async def test_add_azure(self):
        await self.translator.add_provider(Azure(testCreds.azure_keys))
        await self.translator.close()

    async def test_add_google(self):
        await self.translator.add_provider(Google(testCreds.google_credentials, testCreds.google_parent))

    async def test_add_providers(self):
        await self.translator.add_providers(
            Azure(testCreds.azure_keys),
            Google(testCreds.google_credentials, testCreds.google_parent)
        )

    async def test_prefer_azure(self):
        await self.translator.add_providers(
            Azure(testCreds.azure_keys),
            Google(testCreds.google_credentials, testCreds.google_parent)
        )
        provider = self.translator.provider_for('fr', preferred='azure')
        self.assertIsInstance(provider, Azure)

    async def test_prefer_google(self):
        await self.translator.add_providers(
            Azure(testCreds.azure_keys),
            Google(testCreds.google_credentials, testCreds.google_parent)
        )
        provider = self.translator.provider_for('fr', preferred='google')
        self.assertIsInstance(provider, Google)


if __name__ == '__main__':
    unittest.main()
