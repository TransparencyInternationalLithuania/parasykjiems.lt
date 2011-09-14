class SetRemoteAddrMiddleware(object):
    """Set REMOTE_ADDR behind proxy.

    Uses X-Forwarded-For and X-Real-IP, in that order.
    """
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR']
        if 'HTTP_X_REAL_IP' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
