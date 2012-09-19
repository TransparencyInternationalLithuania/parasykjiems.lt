import settings

def expose_settings(request):
    """Allows all templates to access Django settings through the
    SETTINGS variable."""

    return {'SETTINGS': settings}
