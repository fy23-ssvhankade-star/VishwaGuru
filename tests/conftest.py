import httpcore
if not hasattr(httpcore, 'SyncHTTPTransport'):
    httpcore.SyncHTTPTransport = object
