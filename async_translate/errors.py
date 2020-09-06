# Errors and Exceptions

class TranslatorException(Exception):
    """Base exception to be able to catch all exceptions in this module"""
    pass


class ProviderAlreadyAdded(TranslatorException):
    def __init__(self, name):
        super().__init__(f"A provider with the name '{name}' has already been added.")


class NoProvidersAdded(TranslatorException):
    def __init__(self):
        super().__init__("No providers have been added.")


class LanguageNotSupported(TranslatorException):
    def __init__(self, language):
        super().__init__(f"Language {language} is not supported with the current providers.")
