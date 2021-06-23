try:
    from .azure import Azure
except ModuleNotFoundError:
    pass

try:
    from .google import Google
except ModuleNotFoundError:
    pass

try:
    from .deepl import DeepL
except ModuleNotFoundError:
    pass
