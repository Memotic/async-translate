try:
    from .azure import Azure
except ModuleNotFoundError:
    pass

try:
    from .google import Google
except ModuleNotFoundError:
    pass
