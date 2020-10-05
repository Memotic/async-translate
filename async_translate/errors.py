# Errors and Exceptions

class TranslatorException(Exception):
    """Base exception to be able to catch all exceptions in this module"""
    pass


class ProviderAlreadyAdded(TranslatorException):
    def __init__(self, name):
        super().__init__(f"A provider with the name '{name}' has already been added.")


class LanguageNotSupported(TranslatorException):
    def __init__(self, language):
        super().__init__(f"Language {language} is not supported with the current providers.")


class ProvidersMismatch(TranslatorException):
    def __init__(self, language):
        super().__init__(f"From language {language} is not supported with the chosen to provider.")
