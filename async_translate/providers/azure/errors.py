from async_translate.errors import TranslatorException


class AllKeysExhausted(TranslatorException):
    pass


class RequestException(TranslatorException):
    def __init__(self, base, code: int, message: str):
        self.code: int = code
        self.message: str = message
        super().__init__(base)


class NoAPIKeys(TranslatorException):
    pass
