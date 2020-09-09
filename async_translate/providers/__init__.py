try:
    from .azure import Azure
    from .google import Google
except ModuleNotFoundError:
    pass
