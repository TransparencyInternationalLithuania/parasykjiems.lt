class ForceDefaultLanguageMiddleware(object):
    """Ignore Accept-Language HTTP headers

    This will force the I18N machinery to always choose
    settings.LANGUAGE_CODE as the default initial language, unless
    another one is set via sessions or cookies

    Should be installed *before* any middleware that checks
    request.META['HTTP_ACCEPT_LANGUAGE'], namely
    django.middleware.locale.LocaleMiddleware
    """
    def process_request(self, request):
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            del request.META['HTTP_ACCEPT_LANGUAGE']


class SetRemoteAddrMiddleware(object):
    """If X-Real-IP header is set, set REMOTE_ADDR to its contents.

    This should be used if the application is launched behind a remove
    proxy that sets X-Real-IP.
    """
    def process_request(self, request):
        if 'HTTP_X_REAL_IP' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
