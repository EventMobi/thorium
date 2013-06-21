class Request(object):

    def __init__(self, method, identifiers):
        self.method = method.lower()
        self.identifiers = identifiers
