# Errors and Exceptions

class TranslatorException(Exception):
    """Base exception to be able to catch all exceptions in this module"""
    pass


class ProviderAlreadyAdded(TranslatorException):
    def __init__(self, name):
        super().__init__(f"A provider with the name '{name}' has already been added.")


class LanguageNotSupported(TranslatorException):
    def __init__(self, language: str, direction: str = "source"):
        self.language = language
        self.direction = direction
        super().__init__(f"Language {language} is not supported with the current providers.")


class ProvidersMismatch(TranslatorException):
    def __init__(self, language):
        super().__init__(f"From language {language} is not supported with the chosen provider.")


class ProviderUnavailable(TranslatorException):
    def __init__(self, provider, to_language, source_language=None):
        super().__init__()
        self.provider = provider
        self.to_language = to_language
        self.source_language = source_language


class DetectedAsSameError(TranslatorException):
    def __init__(self, to_language, detected_language):
        super().__init__()
        self.to_language = to_language
        self.detected_language = detected_language


class NotEnoughCharacters(TranslatorException):
    def __init__(self, provider: str, characters: int, content_length: int, server_id: int):
        self.provider = provider.title()
        self.characters = characters
        self.content_length = content_length
        self.server_id = server_id

    def __str__(self):
        return "Unable to translate {} characters as the server {} does not have enough characters" \
               " for {}".format(self.content_length, self.server_id, self.provider)
