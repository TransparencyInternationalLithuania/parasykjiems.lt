import settings

class SetRemoteAddrMiddleware(object):
    """Set REMOTE_ADDR behind proxy.

    Uses X-Forwarded-For and X-Real-IP, in that order.
    """
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR']
        elif 'HTTP_X_REAL_IP' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']

class SetHostBehindProxyMiddleware(object):
    """Sets the META HTTP_HOST to the one given in settings if it's localhost.

    Useful if you don't want to use the sites framework for some
    contrib packages that use HTTP_HOST as a fallback, but the actual
    site is behind a reverse proxy, so HTTP_HOST is always localhost.
    """
    def process_request(self, request):
        if request.META['HTTP_HOST'] in ['localhost', '127.0.0.1', '[::1]']:
            request.META['HTTP_HOST'] = settings.SITE_DOMAIN
