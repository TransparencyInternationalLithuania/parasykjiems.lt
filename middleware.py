class SetRemoteAddrMiddleware(object):
    """If X-Real-IP header is set, set REMOTE_ADDR to its contents.

    This should be used if the application is launched behind a remove
    proxy that sets X-Real-IP.
    """
    def process_request(self, request):
        if 'HTTP_X_REAL_IP' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
